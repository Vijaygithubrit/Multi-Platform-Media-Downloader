from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = PROJECT_ROOT / "downloads"


def ensure_download_directory() -> None:
    """Create the downloads directory if it doesn't exist."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_next_number(prefix: str, extension: str) -> int:
    """
    Find the next permanent sequential number.

    Example:
        video1.mp4
        video2.mp4
        video3.mp4

    If video2.mp4 is deleted but video3.mp4 exists,
    the next number will still be 4.
    """

    ensure_download_directory()

    extension = extension.lstrip(".").lower()

    highest_number = 0

    for file in DOWNLOAD_DIR.iterdir():

        if not file.is_file():
            continue

        name = file.name.lower()

        if not name.startswith(prefix.lower()):
            continue

        if file.suffix.lower() != f".{extension}":
            continue

        number_text = name[
            len(prefix):-len(extension)-1
        ]

        if number_text.isdigit():
            highest_number = max(
                highest_number,
                int(number_text)
            )

    return highest_number + 1


def get_next_filename(prefix: str, extension: str) -> Path:
    """
    Generate a unique sequential filename.

    Example:
        get_next_filename("video", "mp4")
        -> downloads/video4.mp4
    """

    number = get_next_number(prefix, extension)

    filename = f"{prefix}{number}.{extension.lstrip('.')}"

    return DOWNLOAD_DIR / filename