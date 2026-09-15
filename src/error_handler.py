from __future__ import annotations


def format_error(error: Exception) -> str:
    """
    Convert an internal exception into a clean user-facing message.
    """

    message = str(error).strip()

    if not message:
        return (
            "The operation failed for an unknown reason."
        )

    lower_message = message.lower()

    # --------------------------------------------------------
    # URL / VALIDATION ERRORS
    # --------------------------------------------------------

    if (
        "invalid url" in lower_message
        or "url" in lower_message
        and "invalid" in lower_message
    ):
        return (
            "The URL is invalid.\n"
            "Please enter a complete HTTP or HTTPS URL."
        )

    # --------------------------------------------------------
    # UNSUPPORTED MEDIA
    # --------------------------------------------------------

    if (
        "unsupported or unknown media" in lower_message
        or "unsupported media type" in lower_message
        or "unsupported website" in lower_message
    ):
        return (
            "This URL is not currently supported.\n"
            "Please try a supported public media URL."
        )

    # --------------------------------------------------------
    # UNAVAILABLE MEDIA
    # --------------------------------------------------------

    if any(
        phrase in lower_message
        for phrase in (
            "video unavailable",
            "video can't be played",
            "video cannot be played",
            "requested format is not available",
            "requested format not available",
            "no formats found",
            "not available",
            "does not exist",
            "has been removed",
            "content is unavailable",
        )
    ):
        return (
            "The requested media is unavailable.\n"
            "It may have been deleted, restricted, or "
            "temporarily unavailable."
        )

    # --------------------------------------------------------
    # PRIVATE / ACCESS RESTRICTIONS
    # --------------------------------------------------------

    if any(
        phrase in lower_message
        for phrase in (
            "private",
            "login required",
            "authentication required",
            "sign in",
            "authentication",
            "logged in",
        )
    ):
        return (
            "This content requires access that the downloader "
            "does not have.\n"
            "Only publicly accessible or authorized content "
            "is supported."
        )

    # --------------------------------------------------------
    # CAPTCHA / DRM
    # --------------------------------------------------------

    if any(
        phrase in lower_message
        for phrase in (
            "captcha",
            "drm",
            "content is protected",
        )
    ):
        return (
            "This content is protected by an access-control "
            "mechanism that this application does not bypass."
        )

    # --------------------------------------------------------
    # NETWORK ERRORS
    # --------------------------------------------------------

    if any(
        phrase in lower_message
        for phrase in (
            "timed out",
            "timeout",
            "connection",
            "network",
            "temporary failure",
            "name resolution",
            "unable to resolve",
        )
    ):
        return (
            "A network error occurred while accessing the media.\n"
            "Please check your internet connection and try again."
        )

    # --------------------------------------------------------
    # FFMPEG / FFPROBE
    # --------------------------------------------------------

    if any(
        phrase in lower_message
        for phrase in (
            "ffmpeg was not found",
            "ffprobe was not found",
            "ffmpeg",
            "ffprobe",
        )
    ):
        return (
            "A media-processing component is unavailable or "
            "could not process the downloaded media.\n"
            "Please verify your FFmpeg installation."
        )

    # --------------------------------------------------------
    # FILE / PERMISSION ERRORS
    # --------------------------------------------------------

    if any(
        phrase in lower_message
        for phrase in (
            "permission denied",
            "access is denied",
            "no space left",
            "disk",
            "could not save",
        )
    ):
        return (
            "The downloaded media could not be saved.\n"
            "Please check your available disk space and "
            "folder permissions."
        )

    # --------------------------------------------------------
    # INSTAGRAM CAROUSEL VIDEO
    # --------------------------------------------------------

    if (
        "carousel" in lower_message
        and "video" in lower_message
        and "implemented soon" in lower_message
    ):
        return message

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return (
        "The operation could not be completed.\n"
        "Please check the URL and try again."
    )