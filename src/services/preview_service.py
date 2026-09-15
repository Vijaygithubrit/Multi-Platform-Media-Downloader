from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import tempfile


# --------------------------------------------------
# PREVIEW DIRECTORY
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

PREVIEW_DIR = PROJECT_ROOT / "temp" / "previews"


# --------------------------------------------------
# SUPPORTED IMAGE TYPES
# --------------------------------------------------

CONTENT_TYPE_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
    "image/bmp": "bmp",
    "image/tiff": "tiff",
    "image/avif": "avif",
}


URL_EXTENSIONS = {
    ".jpg": "jpg",
    ".jpeg": "jpg",
    ".png": "png",
    ".webp": "webp",
    ".gif": "gif",
    ".bmp": "bmp",
    ".tif": "tiff",
    ".tiff": "tiff",
    ".avif": "avif",
}


# --------------------------------------------------
# PREVIEW RESULT
# --------------------------------------------------

class PreviewResult:
    """
    Represents a temporary media preview.
    """

    def __init__(
        self,
        path: Path,
        media_type: str,
        extension: str,
        size: int,
    ):
        self.path = path
        self.media_type = media_type
        self.extension = extension
        self.size = size

    def __repr__(self) -> str:
        return (
            "PreviewResult("
            f"path={self.path!r}, "
            f"media_type={self.media_type!r}, "
            f"extension={self.extension!r}, "
            f"size={self.size!r}"
            ")"
        )


# --------------------------------------------------
# EXTENSION FROM URL
# --------------------------------------------------

def _get_extension_from_url(
    url: str,
) -> str | None:
    """
    Try to determine the image extension from a URL.
    """

    extension = Path(
        urlparse(url).path
    ).suffix.lower()

    return URL_EXTENSIONS.get(
        extension
    )


# --------------------------------------------------
# CREATE PREVIEW DIRECTORY
# --------------------------------------------------

def ensure_preview_directory() -> None:
    """
    Create the temporary preview directory.
    """

    PREVIEW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# --------------------------------------------------
# DOWNLOAD IMAGE PREVIEW
# --------------------------------------------------

def create_image_preview(
    url: str,
    max_size: int = 10 * 1024 * 1024,
) -> PreviewResult:
    """
    Download an image temporarily for preview.

    The image is NOT stored in the permanent
    downloads directory.

    Parameters:
        url:
            Image URL.

        max_size:
            Maximum allowed preview size in bytes.

            Default:
                10 MB

    Returns:
        PreviewResult

    Raises:
        RuntimeError:
            If the URL is not a supported image
            or the download fails.
    """

    ensure_preview_directory()

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

    temp_path: Path | None = None

    try:

        with urlopen(
            request,
            timeout=30,
        ) as response:

            # --------------------------------------------------
            # DETERMINE CONTENT TYPE
            # --------------------------------------------------
            #
            # Real urllib responses normally provide
            # get_content_type().
            #
            # Simple mocked responses may provide a
            # dictionary instead.
            #

            if hasattr(
                response.headers,
                "get_content_type",
            ):

                content_type = (
                    response.headers
                    .get_content_type()
                    .lower()
                )

            else:

                content_type = (
                    response.headers
                    .get("Content-Type", "")
                    .split(";")[0]
                    .strip()
                    .lower()
                )

            # --------------------------------------------------
            # DETERMINE EXTENSION
            # --------------------------------------------------

            extension = (
                CONTENT_TYPE_EXTENSIONS.get(
                    content_type
                )
            )

            # If Content-Type doesn't identify the image,
            # try the URL extension.

            if extension is None:

                extension = (
                    _get_extension_from_url(url)
                )

            if extension is None:

                raise RuntimeError(
                    "The URL does not appear to "
                    "contain a supported image."
                )

            # --------------------------------------------------
            # CREATE TEMPORARY PREVIEW FILE
            # --------------------------------------------------

            with tempfile.NamedTemporaryFile(
                dir=PREVIEW_DIR,
                prefix="preview_",
                suffix=f".{extension}",
                delete=False,
            ) as temp_file:

                temp_path = Path(
                    temp_file.name
                )

                total_size = 0

                while True:

                    chunk = response.read(
                        1024 * 1024
                    )

                    if not chunk:
                        break

                    total_size += len(chunk)

                    # ------------------------------------------
                    # SIZE LIMIT
                    # ------------------------------------------

                    if total_size > max_size:

                        raise RuntimeError(
                            "Preview image exceeds "
                            f"the {max_size} byte limit."
                        )

                    temp_file.write(chunk)

        # --------------------------------------------------
        # VERIFY FILE
        # --------------------------------------------------

        if temp_path is None:

            raise RuntimeError(
                "Preview file could not be created."
            )

        return PreviewResult(
            path=temp_path,
            media_type="image",
            extension=extension,
            size=total_size,
        )

    except RuntimeError:

        if temp_path and temp_path.exists():

            temp_path.unlink()

        raise

    except Exception as error:

        if temp_path and temp_path.exists():

            temp_path.unlink()

        raise RuntimeError(
            f"Image preview failed: {error}"
        ) from error


# --------------------------------------------------
# DELETE PREVIEW
# --------------------------------------------------

def delete_preview(
    preview: PreviewResult | Path,
) -> None:
    """
    Delete a temporary preview file.

    Accepts either:

        PreviewResult

    or:

        Path
    """

    if isinstance(
        preview,
        PreviewResult,
    ):

        preview_path = preview.path

    else:

        preview_path = preview

    try:

        if preview_path.exists():

            preview_path.unlink()

    except Exception as error:

        raise RuntimeError(
            f"Could not delete preview file: "
            f"{error}"
        ) from error


# --------------------------------------------------
# CLEAN ALL PREVIEWS
# --------------------------------------------------

def cleanup_previews() -> int:
    """
    Delete all temporary preview files.

    Returns:
        Number of files deleted.
    """

    if not PREVIEW_DIR.exists():

        return 0

    deleted_count = 0

    for file in PREVIEW_DIR.iterdir():

        if not file.is_file():

            continue

        try:

            file.unlink()

            deleted_count += 1

        except Exception:

            # Continue cleaning other preview files.
            continue

    return deleted_count