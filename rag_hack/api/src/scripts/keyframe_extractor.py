import logging
import subprocess
import re

from pathlib import Path
from datetime import datetime, timedelta
from utils.custom_logging import setup_logging


setup_logging()
logger = logging.getLogger("project_logger")


class KeyframeExtractor:
    def __init__(self) -> None:
        pass

    def _rename_scenes(self, frames, output_dir) -> list[Path]:
        keyframe_paths = []
        for frame in frames:
            current_file_name = Path(
                "{}/{:03d}.png".format(str(output_dir), int(frame["frame"]) + 1))
            scene_time = timedelta(seconds=frame["pts_time"])
            scene_time_string = f"{scene_time}".replace(
                ":", "_").replace(".", "-")
            new_file_path = Path(
                current_file_name.parent, f"{current_file_name.stem}-{scene_time_string}{current_file_name.suffix}")
            current_file_name.rename(new_file_path)
            keyframe_paths.append(new_file_path)
        return keyframe_paths

    def generate_keyframes(self, video_file: Path, output_dir: Path, cutoff_score: str) -> list[Path]:
        """
        Generates keyframes using FFMPEG. A frame is detected as keyframe if it differs 
        more than cutoff score from previous frames. Generated keyframes are renamed to 
        include timestamp at which appears in the original video file.

        Note: video_file path should not contain any spaces

        Args:
            video_file (Path): Path to video file to be processed. Should not contain any spaces in Path.
            output_dir (Path): _description_
            cutoff_score (str): _description_
        """

        output_dir.mkdir(exist_ok=True, parents=True)
        output_time_file = output_dir / "time.txt"
        # command = f'ffmpeg -vf select=gt(scene\,{cutoff_score}),metadata=print:file={str(output_time_file)} -vsync vfr {str(output_dir)}/%03d.png -i'.split()
        command = ['ffmpeg', '-vf', f'select=gt(scene\,{cutoff_score}),metadata=print:file={output_time_file}',
                   '-vsync', 'vfr', f'{output_dir}/%03d.png', '-i', f'{video_file}']
        logger.info(f"executing command: {command}")

        logger.info(f"Generating keyframes for {video_file} with cutoff_score: {cutoff_score}")
        out = subprocess.check_output(command).decode()
        # return out, output_time_file
        # output_time_file = "time.txt"
        frames = self._process_timelines(output_time_file)
        # print(frames)
        keyframe_paths = self._rename_scenes(frames, output_dir)
        keyframes_during_intervals = self._remove_frames_of_same_interval(keyframes=keyframe_paths, interval_duration_seconds=2)
        logger.info(f"Keyframes: {keyframes_during_intervals}")
        return keyframes_during_intervals

    def _process_timelines(self, time_file: Path):
        lines = []
        if time_file.is_file():
            with time_file.open(mode="r") as out_f:
                lines = out_f.readlines()

        frames = []
        last_frame_info = {}
        for line in lines:
            line = line.strip()
            if line.startswith("frame"):
                rex = r"frame:(?P<frame>\d+)\s+pts:(?P<pts>[\d\.]+)\s+pts_time:(?P<pts_time>[\d\.]+)"
                ret = re.match(rex, line)
                if ret:
                    ret_matches = ret.groupdict()
                    last_frame_info["frame"] = int(ret_matches["frame"])
                    last_frame_info["pts"] = float(ret_matches["pts"])
                    last_frame_info["pts_time"] = float(
                        ret_matches["pts_time"])
                else:
                    raise RuntimeError("Wrongly formatted line: " + line)
                continue
            if line.startswith("lavfi.scene_score"):
                splits = line.split("=")
                if len(splits):
                    last_frame_info["score"] = float(splits[1])
                else:
                    raise RuntimeError("Wrongly formatted line: " + line)
                frames.append(last_frame_info)
                last_frame_info = {}
        return frames

    def _time_differs_at_least_t_seconds(self, time_str1, time_str2, t: int):
        format_str = "%H_%M_%S"
        time1 = datetime.strptime(time_str1, format_str)
        time2 = datetime.strptime(time_str2, format_str)
        time_difference = abs(time1 - time2)
        return time_difference >= timedelta(seconds=t)

    def _remove_frames_of_same_interval(self, keyframes: list[Path], interval_duration_seconds: int) -> list[Path]:
        logger.info(f"Removing frames in same interval of {interval_duration_seconds} seconds")
        unique_interval_frame_paths = []
        for frame_file_path in keyframes:
            frame_file_time_str = frame_file_path.stem.split("-")[1]
            unique = True
            for unique_frame_path in unique_interval_frame_paths:
                unique_frame_time_str = unique_frame_path.stem.split("-")[1]
                if not self._time_differs_at_least_t_seconds(frame_file_time_str, unique_frame_time_str, t=interval_duration_seconds):
                    unique = False
                    logger.debug(f"Removing frame: {frame_file_path}")
                    frame_file_path.unlink()
                    break
            if unique:
                unique_interval_frame_paths.append(frame_file_path)
        return unique_interval_frame_paths


