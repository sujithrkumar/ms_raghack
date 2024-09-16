import logging

from utils.custom_logging import setup_logging

setup_logging()
logger = logging.getLogger("project_logger")


def ticks_to_seconds(ticks):
    return ticks / 10_000_000


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{remaining_seconds:05.2f}"
