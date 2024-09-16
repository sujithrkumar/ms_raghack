import logging
import json
from pathlib import Path
import pandas as pd
import os
import time
import azure.cognitiveservices.speech as speechsdk

from utils.util import format_time, ticks_to_seconds
from utils.video_utils import extract_audio, frame_rate_channel, stereo_to_mono
from utils.custom_logging import setup_logging

setup_logging()
logger = logging.getLogger("project_logger")


class AzureSTT:
    def __init__(self, STT_CONFIG: dict) -> None:
        self.speech_config = speechsdk.SpeechConfig(
            subscription=STT_CONFIG['speech_key'], region=STT_CONFIG['speech_region'])
        self.speech_config.speech_recognition_language = STT_CONFIG['speech_recognition_language']
        self.audio_output_dir = STT_CONFIG['audio_output_dir']
        self.transcripts_dir = STT_CONFIG['transcripts_dir']
        self.use_cache = STT_CONFIG['use_cache']
        self.transcripts = []

    def conversation_transcriber_recognition_canceled_cb(self, evt: speechsdk.SessionEventArgs):
        logger.info('Canceled event')

    def conversation_transcriber_session_stopped_cb(self, evt: speechsdk.SessionEventArgs):
        logger.info('SessionStopped event')

    def conversation_transcriber_transcribed_cb(self, evt: speechsdk.SpeechRecognitionEventArgs):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            transcript = evt.result.text
            if transcript:  # Only process if the text is not empty
                start_time_seconds = ticks_to_seconds(evt.result.offset)
                start_time = format_time(start_time_seconds)
                duration = ticks_to_seconds(evt.result.duration)
                end_time = format_time(start_time_seconds + duration)

                speaker_tag = evt.result.speaker_id
                logger.info(f'{speaker_tag} : {start_time} - {end_time}')
                logger.info(transcript)

                self.transcripts.append({
                    "speaker_tag": speaker_tag,
                    "start_time": start_time,
                    "end_time": end_time,
                    "transcript": transcript
                })
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            logger.info('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(
                evt.result.no_match_details))

    def conversation_transcriber_session_started_cb(self, evt: speechsdk.SessionEventArgs):
        logger.info('SessionStarted event')

    def recognize_from_file(self, input_file: Path):
        transcript_file_path = self.transcripts_dir / f"{input_file.stem}.csv"
        if self.use_cache and transcript_file_path.exists():
            logging.info(
                f"Transcript already exists. {str(transcript_file_path)}Reusing since DEV mode is active...")
            return pd.read_csv(transcript_file_path)
        if input_file.suffix not in ['.mp4', '.wav']:
            raise NotImplementedError("Unsupported file type")

        if input_file.suffix in ['.mp4']:
            audio_file_path = extract_audio(video_file_path=input_file,
                                            output_dir=self.audio_output_dir, reuse=self.use_cache)
            self._prepare_audio_file(audio_file_path=audio_file_path)
        else:
            audio_file_path = input_file

        audio_config = speechsdk.audio.AudioConfig(
            filename=str(audio_file_path))
        conversation_transcriber = speechsdk.transcription.ConversationTranscriber(
            speech_config=self.speech_config, audio_config=audio_config)

        transcribing_stop = False

        def stop_cb(evt: speechsdk.SessionEventArgs):
            # """callback that signals to stop continuous recognition upon receiving an event `evt`"""
            logger.info('CLOSING on {}'.format(evt))
            nonlocal transcribing_stop
            transcribing_stop = True

        # Connect callbacks to the events fired by the convesation transcriber
        conversation_transcriber.transcribed.connect(
            self.conversation_transcriber_transcribed_cb)
        conversation_transcriber.session_started.connect(
            self.conversation_transcriber_session_started_cb)
        conversation_transcriber.session_stopped.connect(
            self.conversation_transcriber_session_stopped_cb)
        conversation_transcriber.canceled.connect(
            self.conversation_transcriber_recognition_canceled_cb)
        # stop transcribing on either session stopped or canceled events
        conversation_transcriber.session_stopped.connect(stop_cb)
        conversation_transcriber.canceled.connect(stop_cb)

        conversation_transcriber.start_transcribing_async()

        # Waits for completion.
        while not transcribing_stop:
            time.sleep(.5)

        conversation_transcriber.stop_transcribing_async()
        transcripts_df = pd.DataFrame(self.transcripts)
        transcripts_df.to_csv(transcript_file_path, index=False)

        return transcripts_df

    def _write_transcripts(self, transcript_file_path: Path, transcript):
        with transcript_file_path.open(mode="w+") as f:
            f.write(transcript)

    def _prepare_audio_file(self, audio_file_path: Path):
        self.frame_rate, channels = frame_rate_channel(
            audio_file_path=audio_file_path)

        if channels > 1:
            stereo_to_mono(audio_file_path)
