from src.detector import detect_url
from src.validators import validate_url


def test_url(url: str) -> None:
    print("=" * 70)
    print(f"URL: {url}")
    print("=" * 70)

    # Step 1: Validate URL
    valid, error = validate_url(url)

    if not valid:
        print("VALIDATION : FAIL")
        print(f"ERROR      : {error}")
        return

    print("VALIDATION : PASS")

    # Step 2: Detect media
    try:
        result = detect_url(url)
    except Exception as exc:
        print("DETECTION  : FAIL")
        print(f"ERROR      : {exc}")
        return

    print("DETECTION  : PASS")
    print(f"MEDIA TYPE : {result.media_type}")
    print(f"REASON     : {result.reason}")
    print(f"EXTENSION  : {result.extension}")
    print(f"TITLE      : {result.title}")
    print(f"DURATION   : {result.duration}")
    print(f"EXTRACTOR  : {result.extractor}")
    print(f"HAS VIDEO  : {result.has_video}")
    print(f"HAS AUDIO  : {result.has_audio}")


def main() -> None:
    print("\nUniversal Media Downloader")
    print("Manual Compatibility Test")
    print()

    url = input("Enter a URL to test: ").strip()

    if not url:
        print("ERROR: URL cannot be empty.")
        return

    test_url(url)


if __name__ == "__main__":
    main()
    