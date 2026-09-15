from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from src.file_manager import (
    ensure_download_directory,
    get_next_filename,
)


CONTENT_TYPE_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
    "image/bmp": "bmp",
    "image/tiff": "tiff",
    "image/avif": "avif",
}


def _get_extension_from_url(url: str) -> str | None:
    """
    Try to determine an image extension from the URL.
    """

    path = urlparse(url).path

    extension = Path(path).suffix.lower()

    if extension == ".jpeg":
        return "jpg"

    if extension in {
        ".jpg",
        ".png",
        ".webp",
        ".gif",
        ".bmp",
        ".tiff",
        ".tif",
        ".avif",
    }:
        return extension.lstrip(".")

    return None


def download_image(url: str) -> Path:
    """
    Download an image and assign a generated filename.

    Example:
        image1.jpg
        image2.png
        image3.webp
    """

    ensure_download_directory()

    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0 Safari/537.36"
            )
        },
    )

    try:

        with urlopen(request, timeout=30) as response:

            content_type = (
                response.headers
                .get_content_type()
                .lower()
            )

            # Determine extension from HTTP Content-Type first.
            extension = CONTENT_TYPE_EXTENSIONS.get(
                content_type
            )

            # If Content-Type didn't help, use URL extension.
            if extension is None:

                extension = _get_extension_from_url(url)

            if extension is None:

                raise RuntimeError(
                    "The URL does not appear to point to a supported image."
                )

            final_path = get_next_filename(
                "image",
                extension
            )

            # Download directly to a temporary file first.
            import tempfile

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=f".{extension}"
            ) as temp_file:

                temp_path = Path(temp_file.name)

                while True:

                    chunk = response.read(1024 * 1024)

                    if not chunk:
                        break

                    temp_file.write(chunk)

        # Move only after successful download.
        temp_path.replace(final_path)

        return final_path

    except RuntimeError:
        raise

    except Exception as error:

        raise RuntimeError(
            f"Image download failed: {error}"
        ) from error