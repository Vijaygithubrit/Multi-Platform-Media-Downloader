from pathlib import Path

from src.media_service import detect_media, download_media


def show_detection(result) -> None:
    print()
    print("MEDIA DETECTION")
    print("-" * 50)
    print(f"Media type : {result.media_type}")
    print(f"Reason     : {result.reason}")
    print(f"Extension  : {result.extension}")
    print(f"Title      : {result.title}")
    print(f"Duration   : {result.duration}")
    print(f"Extractor  : {result.extractor}")
    print(f"Has video  : {result.has_video}")
    print(f"Has audio  : {result.has_audio}")


def download_and_report(
    url: str,
    result,
    choice: str | None = None,
) -> None:
    try:
        output_path: Path = download_media(
            url,
            result,
            choice,
        )

        print()
        print("DOWNLOAD SUCCESS")
        print("-" * 50)
        print(f"File : {output_path}")
        print(f"Size : {output_path.stat().st_size:,} bytes")

    except Exception as exc:
        print()
        print("DOWNLOAD FAILED")
        print("-" * 50)
        print(f"Error: {exc}")


def main() -> None:
    print()
    print("Universal Media Downloader")
    print("Manual Download Test")
    print()

    url = input("Enter a URL to download: ").strip()

    if not url:
        print("ERROR: URL cannot be empty.")
        return

    # Detect the media first.
    try:
        result = detect_media(url)
    except Exception as exc:
        print()
        print("DETECTION FAILED")
        print("-" * 50)
        print(f"Error: {exc}")
        return

    show_detection(result)

    # Images do not require a user choice.
    if result.media_type == "image":
        print()
        print("DOWNLOAD TYPE: Image")
        download_and_report(url, result)
        return

    # Audio-only URLs automatically download as audio.
    if result.media_type == "audio":
        print()
        print("DOWNLOAD TYPE: Audio")
        download_and_report(url, result, "audio")
        return

    # Video URLs require the user to choose.
    if result.media_type == "video":
        print()
        print("DOWNLOAD OPTIONS")
        print("-" * 50)
        print("1. Video")
        print("2. Audio")

        choice = input("Choose an option (1/2): ").strip()

        if choice == "1":
            download_and_report(url, result, "video")
        elif choice == "2":
            download_and_report(url, result, "audio")
        else:
            print("ERROR: Invalid choice. Please enter 1 or 2.")

        return

    print()
    print("ERROR: Unsupported media type.")


if __name__ == "__main__":
    main()