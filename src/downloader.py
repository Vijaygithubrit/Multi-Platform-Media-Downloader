from pathlib import Path
import shutil
import tempfile

import yt_dlp

from src.file_manager import (
    ensure_download_directory,
    get_next_filename,
)

from src.processors import (
    check_ffmpeg,
    get_media_streams,
)


# ============================================================
# FIND DOWNLOADED MEDIA FILE
# ============================================================

def _find_downloaded_file(directory: Path) -> Path | None:
    """
    Find the media file created by yt-dlp.
    """

    files = [
        file
        for file in directory.iterdir()
        if file.is_file()
    ]

    if not files:
        return None

    preferred_extensions = {
        ".mp4",
        ".mkv",
        ".webm",
        ".m4a",
        ".mp3",
        ".opus",
        ".aac",
        ".wav",
        ".flac",
    }

    for file in files:
        if file.suffix.lower() in preferred_extensions:
            return file

    return files[0]


# ============================================================
# VIDEO DOWNLOADER
# ============================================================

def download_video(url: str) -> Path:
    """
    Download a highly compatible video.

    Preferred streams:

        H.264 video
             +
        AAC audio
             ↓
           FFmpeg
             ↓
        MP4 container
             ↓
        FFprobe verification
             ↓
        video1.mp4
    """

    ensure_download_directory()

    # --------------------------------------------------------
    # CHECK FFMPEG
    # --------------------------------------------------------

    ffmpeg_available, ffmpeg_info = check_ffmpeg()

    if not ffmpeg_available:
        raise RuntimeError(ffmpeg_info)

    # --------------------------------------------------------
    # GENERATE FINAL FILENAME
    # --------------------------------------------------------

    final_path = get_next_filename(
        "video",
        "mp4"
    )

    # --------------------------------------------------------
    # TEMPORARY DIRECTORY
    # --------------------------------------------------------

    with tempfile.TemporaryDirectory(
        prefix="media_video_"
    ) as temp_dir:

        temp_path = Path(temp_dir)

        # ----------------------------------------------------
        # YT-DLP OPTIONS
        # ----------------------------------------------------

        ydl_options = {

            # Prefer H.264/AVC video + AAC audio.
            #
            # This gives much better compatibility with:
            # - Windows Media Player
            # - VLC
            # - Android phones
            # - iPhones
            # - Telegram
            # - Browsers
            #
            # If that exact combination isn't available,
            # fall back to a compatible MP4 format.
            "format": (
                "bestvideo[vcodec^=avc1]+"
                "bestaudio[acodec^=mp4a]/"
                "best[ext=mp4]/"
                "best"
            ),

            # Final container.
            "merge_output_format": "mp4",

            # Never download playlists.
            "noplaylist": True,

            # Temporary output.
            "outtmpl": str(
                temp_path / "source.%(ext)s"
            ),

            # Explicit FFmpeg location.
            "ffmpeg_location": ffmpeg_info,

            # Terminal output.
            "quiet": False,
            "no_warnings": False,

            # No unnecessary extras.
            "writesubtitles": False,
            "writeautomaticsub": False,
            "writethumbnail": False,

            "keepvideo": False,
        }

        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

        try:

            with yt_dlp.YoutubeDL(
                ydl_options
            ) as ydl:

                ydl.download([url])

        except yt_dlp.utils.DownloadError as error:

            raise RuntimeError(
                f"Video download/merge failed:\n{error}"
            ) from error

        except Exception as error:

            raise RuntimeError(
                f"Unexpected video download error:\n{error}"
            ) from error

        # ----------------------------------------------------
        # FIND FINAL TEMP FILE
        # ----------------------------------------------------

        downloaded_file = _find_downloaded_file(
            temp_path
        )

        if downloaded_file is None:

            raise RuntimeError(
                "yt-dlp finished, but no video file was found."
            )

        # ----------------------------------------------------
        # VERIFY VIDEO + AUDIO
        # ----------------------------------------------------

        try:

            has_video, has_audio = get_media_streams(
                downloaded_file
            )

        except Exception as error:

            raise RuntimeError(
                f"Could not verify the downloaded video:\n{error}"
            ) from error

        # ----------------------------------------------------
        # VIDEO CHECK
        # ----------------------------------------------------

        if not has_video:

            raise RuntimeError(
                "The downloaded file does not contain a video stream."
            )

        # ----------------------------------------------------
        # AUDIO CHECK
        # ----------------------------------------------------

        if not has_audio:

            raise RuntimeError(
                "The downloaded file does not contain an audio stream.\n"
                "The final video was NOT saved."
            )

        # ----------------------------------------------------
        # MOVE TO FINAL LOCATION
        # ----------------------------------------------------

        try:

            shutil.move(
                str(downloaded_file),
                str(final_path)
            )

        except Exception as error:

            raise RuntimeError(
                f"Could not save the final video:\n{error}"
            ) from error

    return final_path


# ============================================================
# AUDIO DOWNLOADER
# ============================================================

def download_audio(url: str) -> Path:
    """
    Download the best available audio and convert it to MP3.

    Final filenames:

        audio1.mp3
        audio2.mp3
        audio3.mp3
    """

    ensure_download_directory()

    # --------------------------------------------------------
    # CHECK FFMPEG
    # --------------------------------------------------------

    ffmpeg_available, ffmpeg_info = check_ffmpeg()

    if not ffmpeg_available:
        raise RuntimeError(ffmpeg_info)

    # --------------------------------------------------------
    # GENERATE FINAL FILENAME
    # --------------------------------------------------------

    final_path = get_next_filename(
        "audio",
        "mp3"
    )

    # --------------------------------------------------------
    # TEMPORARY DIRECTORY
    # --------------------------------------------------------

    with tempfile.TemporaryDirectory(
        prefix="media_audio_"
    ) as temp_dir:

        temp_path = Path(temp_dir)

        # ----------------------------------------------------
        # YT-DLP OPTIONS
        # ----------------------------------------------------

        ydl_options = {

            # Best available audio.
            "format": "bestaudio/best",

            # No playlists.
            "noplaylist": True,

            # Temporary output.
            "outtmpl": str(
                temp_path / "source.%(ext)s"
            ),

            # Explicit FFmpeg.
            "ffmpeg_location": ffmpeg_info,

            "quiet": False,
            "no_warnings": False,

            # Don't download unnecessary extras.
            "writesubtitles": False,
            "writeautomaticsub": False,
            "writethumbnail": False,

            "keepvideo": False,

            # Convert to MP3.
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

        try:

            with yt_dlp.YoutubeDL(
                ydl_options
            ) as ydl:

                ydl.download([url])

        except yt_dlp.utils.DownloadError as error:

            raise RuntimeError(
                f"Audio download failed:\n{error}"
            ) from error

        except Exception as error:

            raise RuntimeError(
                f"Unexpected audio download error:\n{error}"
            ) from error

        # ----------------------------------------------------
        # FIND AUDIO
        # ----------------------------------------------------

        downloaded_file = _find_downloaded_file(
            temp_path
        )

        if downloaded_file is None:

            raise RuntimeError(
                "yt-dlp finished, but no audio file was found."
            )

        # ----------------------------------------------------
        # MOVE FINAL AUDIO
        # ----------------------------------------------------

        try:

            shutil.move(
                str(downloaded_file),
                str(final_path)
            )

        except Exception as error:

            raise RuntimeError(
                f"Could not save the final audio:\n{error}"
            ) from error

    return final_path