from pathlib import Path
from urllib.parse import urlparse

from src.error_handler import format_error
from src.media_service import detect_media, download_media
from src.platforms.instagram import (
    extract_instagram_post,
    download_instagram_item,
)
from src.services.carousel_service import CarouselSession
from src.services.preview_service import (
    create_image_preview,
    delete_preview,
    cleanup_previews,
)


# ============================================================
# APPLICATION SETTINGS
# ============================================================

APP_NAME = "Universal Media Downloader"


# ============================================================
# DISPLAY HELPERS
# ============================================================

def print_header() -> None:
    print()
    print("=" * 60)
    print("             UNIVERSAL MEDIA DOWNLOADER")
    print("=" * 60)
    print("Paste a supported public media URL to begin.")
    print("Type 'exit' to close the application.")
    print("=" * 60)
    print()


def print_separator() -> None:
    print("-" * 60)


def print_success(path: Path) -> None:
    print()
    print("DOWNLOAD SUCCESS")
    print_separator()
    print(f"File : {path}")
    print(f"Size : {path.stat().st_size:,} bytes")
    print()


# ============================================================
# URL HELPERS
# ============================================================

def is_instagram_url(url: str) -> bool:
    """
    Check whether the supplied URL belongs to Instagram.
    """

    try:
        hostname = urlparse(url).hostname

        if not hostname:
            return False

        hostname = hostname.lower()

        return (
            hostname == "instagram.com"
            or hostname.endswith(".instagram.com")
        )

    except Exception:
        return False


# ============================================================
# USER INPUT
# ============================================================

def ask_video_choice() -> str:
    """
    Ask whether the user wants video or audio.
    """

    while True:
        print()
        print("This URL contains video.")
        print()
        print("1. Video")
        print("2. Audio")
        print()

        choice = input("Choose an option (1/2): ").strip()

        if choice == "1":
            return "video"

        if choice == "2":
            return "audio"

        print()
        print("Invalid choice. Please enter 1 or 2.")


# ============================================================
# STANDARD MEDIA DOWNLOAD
# ============================================================

def process_standard_url(url: str) -> None:
    """
    Process normal media URLs through the main media service.
    """

    print()
    print("Detecting media...")
    print_separator()

    result = detect_media(url)

    print(f"Media type : {result.media_type}")

    if result.title:
        print(f"Title      : {result.title}")

    if result.duration:
        print(f"Duration   : {result.duration}")

    if result.extractor:
        print(f"Extractor  : {result.extractor}")

    if result.media_type == "video":

        choice = ask_video_choice()

        print()
        print(
            "Downloading video..."
            if choice == "video"
            else "Downloading audio..."
        )

        output_path = download_media(
            url,
            result,
            choice=choice,
        )

    else:

        print()
        print("Downloading...")

        output_path = download_media(
            url,
            result,
        )

    print_success(output_path)


# ============================================================
# INSTAGRAM SINGLE ITEM
# ============================================================

def process_instagram_single(result) -> None:
    """
    Process a single Instagram image or video.
    """

    item = result.items[0]

    print()
    print("Instagram media detected.")
    print_separator()
    print(f"Media type : {item.media_type}")

    if item.media_type == "image":

        print()
        print("Downloading image...")

        output_path = download_instagram_item(item)

        print_success(output_path)
        return

    if item.media_type == "video":

        choice = ask_video_choice()

        print()
        print(
            "Downloading video..."
            if choice == "video"
            else "Downloading audio..."
        )

        output_path = download_instagram_item(
            item,
            choice=choice,
        )

        print_success(output_path)
        return

    raise RuntimeError(
        f"Unsupported Instagram media type: {item.media_type}"
    )


# ============================================================
# INSTAGRAM CAROUSEL DISPLAY
# ============================================================

def print_carousel_items(session: CarouselSession) -> None:
    """
    Display the current carousel state.
    """

    result = session.result

    print()
    print("=" * 60)
    print("                 INSTAGRAM CAROUSEL")
    print("=" * 60)

    print(f"Shortcode : {result.shortcode}")
    print(f"Total     : {session.total_items}")
    print(f"Downloaded: {session.downloaded_count}")

    print_separator()

    for item in result.items:

        status = ""

        if item.index in session.downloaded_indices:
            status = " [DOWNLOADED]"

        elif item.index in session.unsupported_indices:
            status = " [VIDEO - UNSUPPORTED]"

        print(
            f"{item.index}. "
            f"{item.media_type.upper()}"
            f"{status}"
        )

    print_separator()


# ============================================================
# CAROUSEL SELECTION INPUT
# ============================================================

def ask_indices() -> list[int] | None:
    """
    Read a comma-separated list of carousel item numbers.

    Example:
        1,3,5
    """

    value = input(
        "Enter item numbers (example: 1,3,5): "
    ).strip()

    if not value:
        return None

    try:
        indices = [
            int(part.strip())
            for part in value.split(",")
            if part.strip()
        ]

        return indices

    except ValueError:
        print()
        print(
            "Invalid selection. Use numbers separated by commas."
        )
        return None


# ============================================================
# CAROUSEL PREVIEW
# ============================================================

def preview_carousel_item(
    session: CarouselSession,
    index: int,
) -> None:
    """
    Create and display information about an image preview.

    The preview service creates a temporary preview file.
    """

    item = session.get_item(index)

    if item.media_type != "image":
        print()
        print(
            f"Instagram carousel item {index} is a video."
        )
        print(
            "Video preview will be implemented soon."
        )
        return

    print()
    print(f"Creating preview for item {index}...")

    preview = create_image_preview(item.url)

    try:
        print()
        print("PREVIEW CREATED")
        print_separator()
        print(f"Item   : {index}")
        print(f"File   : {preview.path}")

        if preview.content_type:
            print(
                f"Type   : {preview.content_type}"
            )

        if preview.size:
            print(
                f"Size   : {preview.size:,} bytes"
            )

        print_separator()
        print(
            "The preview file is temporary and will be "
            "cleaned automatically."
        )

    finally:
        delete_preview(preview.path)


# ============================================================
# CAROUSEL DOWNLOAD
# ============================================================

def download_carousel_selection(
    session: CarouselSession,
    indices: list[int],
) -> None:
    """
    Download selected carousel items.
    """

    print()
    print("Validating selection...")

    session.validate_selection(indices)

    print()
    print("Downloading selected items...")
    print_separator()

    downloaded = session.download_selected(indices)

    for path in downloaded:
        print()
        print(f"✓ Downloaded: {path.name}")

    print()
    print(
        f"Successfully downloaded "
        f"{len(downloaded)} item(s)."
    )


# ============================================================
# CAROUSEL MAIN LOOP
# ============================================================

def process_instagram_carousel(result) -> None:
    """
    Interactive Instagram carousel workflow.
    """

    session = CarouselSession(result)

    while True:

        print_carousel_items(session)

        if session.is_complete:
            print()
            print("All currently supported carousel items are downloaded.")
            print()

            choice = input(
                "Press Enter to return, or type 'exit': "
            ).strip().lower()

            if choice == "exit":
                return

            return

        print()
        print("CAROUSEL OPTIONS")
        print_separator()

        print("1. Download All Supported")
        print("2. Select Items")
        print("3. Preview Item")
        print("4. Download Remaining")
        print("5. Exit")

        print_separator()

        choice = input(
            "Choose an option (1-5): "
        ).strip()

        # ----------------------------------------------------
        # DOWNLOAD ALL
        # ----------------------------------------------------

        if choice == "1":

            try:
                downloaded = session.download_all()

                print()

                if downloaded:
                    for path in downloaded:
                        print(f"✓ Downloaded: {path.name}")

                    print()
                    print(
                        f"Successfully downloaded "
                        f"{len(downloaded)} item(s)."
                    )

                else:
                    print(
                        "No supported items are available "
                        "for download."
                    )

            except Exception as error:
                print()
                print("DOWNLOAD ERROR")
                print_separator()
                print(error)

        # ----------------------------------------------------
        # SELECT ITEMS
        # ----------------------------------------------------

        elif choice == "2":

            indices = ask_indices()

            if indices is None:
                continue

            try:
                download_carousel_selection(
                    session,
                    indices,
                )

            except Exception as error:
                print()
                print("SELECTION ERROR")
                print_separator()
                print(error)

        # ----------------------------------------------------
        # PREVIEW
        # ----------------------------------------------------

        elif choice == "3":

            try:
                value = input(
                    "Enter item number to preview: "
                ).strip()

                index = int(value)

                preview_carousel_item(
                    session,
                    index,
                )

            except ValueError as error:
                print()
                print("PREVIEW ERROR")
                print_separator()
                print(error)

            except Exception as error:
                print()
                print("PREVIEW ERROR")
                print_separator()
                print(error)

        # ----------------------------------------------------
        # DOWNLOAD REMAINING
        # ----------------------------------------------------

        elif choice == "4":

            try:
                downloaded = session.download_remaining()

                print()

                if downloaded:
                    for path in downloaded:
                        print(f"✓ Downloaded: {path.name}")

                    print()
                    print(
                        f"Successfully downloaded "
                        f"{len(downloaded)} item(s)."
                    )

                else:
                    print(
                        "No remaining supported items."
                    )

            except Exception as error:
                print()
                print("DOWNLOAD ERROR")
                print_separator()
                print(error)

        # ----------------------------------------------------
        # EXIT CAROUSEL
        # ----------------------------------------------------

        elif choice == "5":

            print()
            print("Leaving Instagram carousel.")
            return

        else:

            print()
            print(
                "Invalid option. Please choose 1-5."
            )


# ============================================================
# INSTAGRAM PROCESSOR
# ============================================================

def process_instagram_url(url: str) -> None:
    """
    Process an Instagram URL.
    """

    print()
    print("Instagram URL detected.")
    print("Extracting Instagram media...")
    print_separator()

    result = extract_instagram_post(url)

    print(f"Post type : {result.post_type}")
    print(f"Shortcode : {result.shortcode}")
    print(f"Items     : {len(result.items)}")

    # --------------------------------------------------------
    # SINGLE POST
    # --------------------------------------------------------

    if result.post_type == "single":

        process_instagram_single(result)
        return

    # --------------------------------------------------------
    # CAROUSEL
    # --------------------------------------------------------

    if result.post_type == "carousel":

        process_instagram_carousel(result)
        return

    raise RuntimeError(
        f"Unsupported Instagram post type: "
        f"{result.post_type}"
    )


# ============================================================
# MAIN URL PROCESSOR
# ============================================================

def process_url(url: str) -> None:
    """
    Route a URL to the appropriate downloader.
    """

    if is_instagram_url(url):

        process_instagram_url(url)

    else:

        process_standard_url(url)


# ============================================================
# APPLICATION LOOP
# ============================================================

def main() -> None:
    """
    Start the Universal Media Downloader.
    """

    cleanup_previews()

    print_header()

    while True:

        try:

            url = input("Enter URL: ").strip()

            if not url:
                print()
                print("Please enter a URL.")
                continue

            if url.lower() in {
                "exit",
                "quit",
                "q",
            }:
                print()
                print("Goodbye! 👋")
                break

            print()

            process_url(url)

            print_separator()

        except KeyboardInterrupt:

            print()
            print()
            print("Application stopped.")
            break

        except EOFError:

            print()
            print()
            print("Application stopped.")
            break

        except Exception as error:

            print()
            print("=" * 60)
            print("DOWNLOAD FAILED")
            print("=" * 60)
            print()
            print("❌ The operation could not be completed.")
            print()
            print("Reason:")
            print(format_error(error))
            print()
            print(
                "The application is still running. "
                "You can try another URL."
            )
            print("=" * 60)
            print()

        finally:

            cleanup_previews()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()