from datetime import datetime, timedelta
import json
import logging
import re
import pandas as pd
from pathlib import Path

from core.nlp.chunk_enhancer import get_keyframes_description
from scripts.keyframe_extractor import KeyframeExtractor
from core.speech_processor.azure_stt import AzureSTT
from config import KG_CHUNKING_CONFIG, STT_CONFIG, CHUNKING_CONFIG, VIDEO_INSIGHTS_CONFIG, BLOB_CONF
from utils.custom_logging import setup_logging
from utils.storage_manager import AzureBLOB

setup_logging()
logger = logging.getLogger("project_logger")


def transcript_time_string_to_seconds(time_str):
    """Function to convert time strings like "00:03:58.67" to seconds

    Args:
        time_str (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Convert to a datetime object
    time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
    # Calculate total seconds
    total_seconds = time_obj.hour * 3600 + time_obj.minute * \
        60 + time_obj.second + time_obj.microsecond / 1e6
    return total_seconds


def keyframe_time_string_to_seconds(custom_str):
    """Function to convert time strings like "0_00_03" to seconds

    Args:
        custom_str (_type_): _description_

    Returns:
        _type_: _description_
    """
    hours, minutes, seconds = map(int, custom_str.split('_'))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds

def get_speaker_sentence_transcripts(raw_transcripts_df: pd.DataFrame):
    speaker_sentence_transcripts = []
    # TODO: end_time and start_time may not be accurate
    for index, transcript_details in raw_transcripts_df.iterrows():
        speaker_sentence_transcripts.extend(
            [
                {
                    "speaker_tag": transcript_details['speaker_tag'],
                    "start_time": transcript_details['start_time'],
                    "end_time": transcript_details['end_time'],
                    "transcript": sentence.strip()
                }
                for sentence in re.split("\\.|,|\n", transcript_details['transcript']) if sentence.strip()
            ]
        )
    return pd.DataFrame(speaker_sentence_transcripts)


def create_chunks(sentence_transcripts_df: pd.DataFrame, CHUNK_LENGTH: int, STRIDE: int):
    """
    Create a chunk(group) of sentences of window size CHUNK_LENGTH where every chunk
    will have an overlap of STRIDE number of sentences.

    Args:
        sentence_transcripts_df (pd.DataFrame): _description_
        CHUNK_LENGTH (int): _description_
        STRIDE (int): _description_

    Returns:
        _type_: _description_
    """
    logger.info(
        f"Creating chunks with Chunk Length: {CHUNK_LENGTH}, Stride: {STRIDE}")
    chunks = []
    chunk_number = 0
    for i in range(0, len(sentence_transcripts_df), (CHUNK_LENGTH - STRIDE)):
        chunk = sentence_transcripts_df.iloc[i:i+CHUNK_LENGTH]

        chunks.append({
            # 'start_sentence_num': chunk['sentence_num'].iloc[0],
            # 'end_sentence_num': chunk['sentence_num'].iloc[-1],
            'chunk_number': chunk_number,
            'speaker_tags': chunk['speaker_tag'].tolist(),
            'transcripts': chunk['transcript'].tolist(),
            'start_times': chunk['start_time'].tolist(),
            'end_times': chunk['end_time'].tolist()
        })
        chunk_number += 1
    logger.info(f"Total Number of Chunks: {len(chunks)}")
    chunks_df = pd.DataFrame(chunks)
    return chunks_df


def get_chunked_transcripts(video_name: str, chunks_df: pd.DataFrame) -> list:
    """Converts the chunks into the format where each chunk contains speaker_name: transcripts data for each chunk

    Args:
        chunks_df (pd.DataFrame): _description_

    Returns:
        list: list of transcript chunks in the format "Speaker Tag: Transcripts"
    """
    logger.info(f"Creating chunked transcripts")
    chunked_transcripts = []
    for index, chunk in chunks_df.iterrows():
        chunked_transcript = ""
        transcripts = chunk['transcripts']
        previous_speaker_tag = -1
        for i in range(len(transcripts)):
            if chunk['speaker_tags'][i] != previous_speaker_tag:
                chunked_transcript += f"\n{chunk['speaker_tags'][i]}:  {chunk['transcripts'][i]}"
            else:
                chunked_transcript += f". {chunk['transcripts'][i]}"
            previous_speaker_tag = chunk['speaker_tags'][i]

        chunked_transcript = chunked_transcript.strip()
        chunked_transcripts.append({
            "video_path": video_name,
            "video_name": video_name,
            "chunk_number": chunk['chunk_number'],
            "start_time": chunk['start_times'][0],
            "end_time": chunk['end_times'][-1],
            "transcripts": chunked_transcript
        })

    return chunked_transcripts


def extract_keyframes(video_file_path: Path):
    keyframes_dir = VIDEO_INSIGHTS_CONFIG['keyframes_dir'] / \
        video_file_path.stem
    logger.info(f"Generating keyframes to {keyframes_dir}")
    keyframe_extractor = KeyframeExtractor()
    return keyframe_extractor.generate_keyframes(video_file=video_file_path, output_dir=keyframes_dir, cutoff_score=VIDEO_INSIGHTS_CONFIG['keyframe_cutoff_score'])


def get_chunked_transcripts_with_keyframes(chunked_transcripts: list, keyframe_path_to_blob_path: dict):

    # TODO: not handled the case where keyframe can appear before transcription start and after transcription ends
    chunked_transcripts_with_keyframes = []

    first_chunk = True
    for chunked_transcript in chunked_transcripts:
        chunk_start_time_seconds = transcript_time_string_to_seconds(
            chunked_transcript['start_time'])
        chunk_end_time_seconds = transcript_time_string_to_seconds(
            chunked_transcript['end_time'])

        chunk_keyframe_paths = []
        chunk_keyframe_blob_paths = []
        for keyframe_path, keyframe_blob_path in keyframe_path_to_blob_path.items():
            keyframe_time_seconds = keyframe_time_string_to_seconds(
                keyframe_path.stem.split('-')[1])
            if chunk_start_time_seconds <= keyframe_time_seconds <= chunk_end_time_seconds:
                chunk_keyframe_blob_paths.append(str(keyframe_blob_path))
                chunk_keyframe_paths.append(str(keyframe_path))
            elif first_chunk and keyframe_time_seconds <= chunk_start_time_seconds:
                chunk_keyframe_blob_paths.append(str(keyframe_blob_path))
                chunk_keyframe_paths.append(str(keyframe_path))
        first_chunk = False


        chunked_transcript['keyframe_paths'] = chunk_keyframe_paths
        chunked_transcript['keyframe_blob_paths'] = chunk_keyframe_blob_paths
        if chunk_keyframe_paths:
            chunked_transcript['keyframes_description'] = get_keyframes_description(
                transcripts=chunked_transcript['transcripts'],
                keyframe_paths=chunk_keyframe_paths
            )
        else:
            chunked_transcript['keyframes_description'] = ""
        chunked_transcripts_with_keyframes.append(
            chunked_transcript
        )

    return chunked_transcripts_with_keyframes


def upload_keyframes(video_name: str, keyframe_paths: list) -> list:
    keyframe_blob_paths = []
    storage_manager = AzureBLOB(BLOB_CONF=BLOB_CONF)
    for keyframe_path in keyframe_paths:
        keyframe_blob_path = storage_manager.upload(
            container_name=BLOB_CONF['keyframe_container'], blob_name=f"{video_name}/{keyframe_path.name}", file_path=keyframe_path)
        keyframe_blob_paths.append(keyframe_blob_path)
    return keyframe_blob_paths


def get_video_chunks(input_file: Path):
    azure_stt = AzureSTT(STT_CONFIG=STT_CONFIG)
    logger.info(f"Speech to text conversion in progress...")
    transcripts_df = azure_stt.recognize_from_file(input_file=input_file)
    logger.info(f"Creating chunks from transcripts...")
    chunks_df = create_chunks(sentence_transcripts_df=transcripts_df,
                              CHUNK_LENGTH=CHUNKING_CONFIG["chunk_length"],
                              STRIDE=CHUNKING_CONFIG["stride"])

    chunked_transcripts = get_chunked_transcripts(
        video_name=input_file.name, chunks_df=chunks_df)
    logger.info(json.dumps(chunked_transcripts, indent=4))

    logger.info(f"Extracting keyframes...")
    keyframe_paths = extract_keyframes(video_file_path=input_file)
    keyframe_blob_paths = upload_keyframes(
        video_name=input_file.name, keyframe_paths=keyframe_paths)
    keyframe_path_to_blob_path = {keyframe_path: keyframe_blob_path for keyframe_path,
                                  keyframe_blob_path in zip(keyframe_paths, keyframe_blob_paths)}

    logger.info(json.dumps(
        [str(keyframe_path) for keyframe_path in keyframe_paths], indent=4))

    chunked_transcripts_with_keyframes = get_chunked_transcripts_with_keyframes(
        chunked_transcripts, keyframe_path_to_blob_path)

    logger.info(json.dumps(chunked_transcripts_with_keyframes, indent=4))
    return chunked_transcripts_with_keyframes


def get_video_chunks_for_kg(input_file: Path):
    azure_stt = AzureSTT(STT_CONFIG=STT_CONFIG)
    logger.info(f"Speech to text conversion in progress...")
    transcripts_df = azure_stt.recognize_from_file(input_file=input_file)
    logger.info(f"Creating chunks from transcripts...")
    chunks_df = create_chunks(sentence_transcripts_df=transcripts_df,
                              CHUNK_LENGTH=KG_CHUNKING_CONFIG["chunk_length"],
                              STRIDE=KG_CHUNKING_CONFIG["stride"])
    # chunks_df = chunks_df.head(n=1)

    chunked_transcripts = get_chunked_transcripts(
        video_name=input_file.name, chunks_df=chunks_df)
    logger.info(json.dumps(chunked_transcripts, indent=4))
    return chunked_transcripts
