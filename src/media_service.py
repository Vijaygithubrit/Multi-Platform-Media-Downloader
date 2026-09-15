from pathlib import Path

from src.detector import DetectionResult, detect_url
from src.downloader import download_audio, download_video
from src.image_downloader import download_image
from src.validators import validate_url


def detect_media(url: str) -> DetectionResult:
    """
    Validate and detect the media type of a URL.

    This function does not download anything.
    """

    valid, error = validate_url(url)

    if not valid:
        raise ValueError(
            f"Invalid URL: {error}"
        )

    result = detect_url(url)

    if result.media_type == "unknown":
        raise RuntimeError(
            f"Unsupported or unknown media: {result.reason}"
        )

    return result


def download_media(
    url: str,
    result: DetectionResult,
    choice: str | None = None,
) -> Path:
    """
    Download media according to the detected media type.

    Rules:

        Image:
            Automatically downloads the image.

        Audio:
            Automatically downloads audio.

        Video:
            Requires a choice:
                "video" -> download video
                "audio" -> download audio
    """

    # --------------------------------------------------
    # IMAGE
    # --------------------------------------------------

    if result.media_type == "image":

        return download_image(url)

    # --------------------------------------------------
    # AUDIO
    # --------------------------------------------------

    if result.media_type == "audio":

        return download_audio(url)

    # --------------------------------------------------
    # VIDEO
    # --------------------------------------------------

    if result.media_type == "video":

        if choice is None:
            raise ValueError(
                "A download choice is required for video: "
                "'video' or 'audio'."
            )

        choice = choice.lower().strip()

        if choice == "video":

            return download_video(url)

        if choice == "audio":

            return download_audio(url)

        raise ValueError(
            "Invalid video download choice. "
            "Use 'video' or 'audio'."
        )

    # --------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------

    raise RuntimeError(
        f"Unsupported media type: {result.media_type}"
    )


def process_url(
    url: str,
    choice: str | None = None,
) -> Path:
    """
    Complete media processing workflow.

    Flow:

        URL
         ↓
        Validate
         ↓
        Detect
         ↓
        Download
         ↓
        Return final file path

    For images and audio, no choice is required.

    For videos, choice must be:
        "video"
        or
        "audio"
    """

    result = detect_media(url)

    return download_media(
        url,
        result,
        choice,
    )