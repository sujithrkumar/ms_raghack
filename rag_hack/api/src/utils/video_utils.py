import logging
import wave

from pathlib import Path
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from utils.custom_logging import setup_logging


setup_logging()
logger = logging.getLogger("project_logger")


def frame_rate_channel(audio_file_path):
    with wave.open(str(audio_file_path), "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate, channels


def upload_blob(bucket_name, source_file_name, destination_blob_name, use_existing: bool = False):
    """Uploads a file to the bucket."""
    raise NotImplementedError()


def stereo_to_mono(audio_file_path):
    logging.info("Converting sterio to mono...")
    sound = AudioSegment.from_wav(audio_file_path)
    sound = sound.set_channels(1)
    sound.export(audio_file_path, format="wav")
    logging.info(f"Sterio to mono convertion complete: {str(audio_file_path)}")


def mp3_to_wav(audio_file_name):
    if audio_file_name.split('.')[1] == 'mp3':
        sound = AudioSegment.from_mp3(audio_file_name)
        audio_file_name = audio_file_name.split('.')[0] + '.wav'
        sound.export(audio_file_name, format="wav")


def extract_audio(video_file_path: Path, output_dir: Path, output_ext: str = "wav", reuse: bool = False) -> Path:
    """Converts video to audio using MoviePy library
    that uses `ffmpeg` under the hood"""
    logging.info(f"Extracting audio from video: {video_file_path}")
    audio_file_path = output_dir / \
        f"{video_file_path.stem}.{output_ext}"

    if reuse and audio_file_path.exists():
        logging.info(
            f"Audio file already exists. Reusing the same ({str(audio_file_path)})...")
        return audio_file_path

    clip = VideoFileClip(str(video_file_path))
    logging.info(f"Extracting audio from video ({str(video_file_path)})...")
    clip.audio.write_audiofile(str(audio_file_path))
    logging.info(f'Audio ({str(audio_file_path)}) extraction completed')

    return audio_file_path
