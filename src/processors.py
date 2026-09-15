import shutil
import subprocess
from pathlib import Path


def check_ffmpeg() -> tuple[bool, str]:
    """
    Check whether FFmpeg is available.
    """

    ffmpeg_path = shutil.which("ffmpeg")

    if ffmpeg_path is None:
        return (
            False,
            "FFmpeg was not found on PATH."
        )

    return True, ffmpeg_path


def check_ffprobe() -> tuple[bool, str]:
    """
    Check whether FFprobe is available.
    """

    ffprobe_path = shutil.which("ffprobe")

    if ffprobe_path is None:
        return (
            False,
            "FFprobe was not found on PATH."
        )

    return True, ffprobe_path


def get_media_streams(file_path: Path) -> tuple[bool, bool]:
    """
    Inspect a media file using FFprobe.

    Returns:
        (has_video, has_audio)
    """

    ffprobe_available, ffprobe_info = check_ffprobe()

    if not ffprobe_available:
        raise RuntimeError(ffprobe_info)

    command = [
        ffprobe_info,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_type",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(file_path),
    ]

    video_result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    has_video = (
        "video" in video_result.stdout.lower()
    )

    command = [
        ffprobe_info,
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=codec_type",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(file_path),
    ]

    audio_result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    has_audio = (
        "audio" in audio_result.stdout.lower()
    )

    return has_video, has_audio