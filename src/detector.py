from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp


# --------------------------------------------------
# DETECTION RESULT
# --------------------------------------------------

@dataclass
class DetectionResult:
    media_type: str
    reason: str
    extension: str | None = None

    # Information obtained from yt-dlp
    title: str | None = None
    duration: int | None = None
    extractor: str | None = None

    has_video: bool = False
    has_audio: bool = False


# --------------------------------------------------
# DIRECT IMAGE EXTENSIONS
# --------------------------------------------------

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".bmp",
    ".tiff",
    ".tif",
    ".avif",
}


# --------------------------------------------------
# DIRECT IMAGE DETECTION
# --------------------------------------------------

def detect_direct_image(url: str) -> DetectionResult | None:
    """
    Detect URLs that directly point to image files.

    Example:
        https://example.com/photo.jpg

    This check happens before yt-dlp because a direct image
    URL should be treated as an image automatically.
    """

    parsed = urlparse(url)

    path = Path(parsed.path)

    extension = path.suffix.lower()

    if extension in IMAGE_EXTENSIONS:

        # Normalize JPEG to JPG for our final filename.
        if extension == ".jpeg":
            extension = ".jpg"

        return DetectionResult(
            media_type="image",
            reason="URL directly points to an image file.",
            extension=extension.lstrip("."),
            has_video=False,
            has_audio=False,
        )

    return None


# --------------------------------------------------
# YT-DLP MEDIA DETECTION
# --------------------------------------------------

def detect_with_ytdlp(url: str) -> DetectionResult:
    """
    Ask yt-dlp for metadata without downloading the media.

    This allows us to determine whether the URL contains
    video, audio, or both.
    """

    ydl_options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_options) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

    except yt_dlp.utils.DownloadError as error:

        return DetectionResult(
            media_type="unknown",
            reason=f"yt-dlp could not process this URL: {error}",
        )

    except Exception as error:

        return DetectionResult(
            media_type="unknown",
            reason=f"Unexpected detection error: {error}",
        )

    if not info:

        return DetectionResult(
            media_type="unknown",
            reason="No media information was returned.",
        )

    # --------------------------------------------------
    # BASIC INFORMATION
    # --------------------------------------------------

    title = info.get("title")

    duration = info.get("duration")

    extractor = (
        info.get("extractor_key")
        or info.get("extractor")
    )

    # --------------------------------------------------
    # CHECK AVAILABLE FORMATS
    # --------------------------------------------------

    formats = info.get("formats") or []

    has_video = False
    has_audio = False

    for media_format in formats:

        video_codec = media_format.get("vcodec")
        audio_codec = media_format.get("acodec")

        if video_codec and video_codec != "none":
            has_video = True

        if audio_codec and audio_codec != "none":
            has_audio = True

    # --------------------------------------------------
    # SOME EXTRACTORS PROVIDE CODECS DIRECTLY
    # --------------------------------------------------

    if info.get("vcodec") and info.get("vcodec") != "none":
        has_video = True

    if info.get("acodec") and info.get("acodec") != "none":
        has_audio = True

    # --------------------------------------------------
    # DETERMINE MEDIA TYPE
    # --------------------------------------------------

    if has_video:

        return DetectionResult(
            media_type="video",
            reason="Video media detected by yt-dlp.",
            title=title,
            duration=duration,
            extractor=extractor,
            has_video=True,
            has_audio=has_audio,
        )

    if has_audio:

        return DetectionResult(
            media_type="audio",
            reason="Audio-only media detected by yt-dlp.",
            title=title,
            duration=duration,
            extractor=extractor,
            has_video=False,
            has_audio=True,
        )

    return DetectionResult(
        media_type="unknown",
        reason="yt-dlp found the URL but could not identify video or audio streams.",
        title=title,
        duration=duration,
        extractor=extractor,
        has_video=False,
        has_audio=False,
    )


# --------------------------------------------------
# MAIN DETECTOR
# --------------------------------------------------

def detect_url(url: str) -> DetectionResult:
    """
    Main media detection function.

    Detection order:

        1. Direct image detection
        2. yt-dlp detection
        3. Unknown / unsupported
    """

    # First check whether this is a direct image.
    image_result = detect_direct_image(url)

    if image_result:
        return image_result

    # Otherwise ask yt-dlp.
    return detect_with_ytdlp(url)