import sys
from pathlib import Path


# --------------------------------------------------
# PROJECT PATH
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.platforms.instagram import extract_instagram_post


# --------------------------------------------------
# TEST URL
# --------------------------------------------------

URL = (
    "https://www.instagram.com/p/DdTdMsdDe7E/"
    "?utm_source=ig_web_copy_link"
    "&stkn=MzRlODBiNWFlZA=="
)


# --------------------------------------------------
# MAIN TEST
# --------------------------------------------------

def main():

    print("=" * 70)
    print("INSTAGRAM MIXED CAROUSEL TEST")
    print("=" * 70)

    try:

        print("\n🔍 Reading Instagram post...\n")

        result = extract_instagram_post(URL)

        print(f"Post type : {result.post_type}")
        print(f"Shortcode : {result.shortcode}")
        print(f"Items     : {len(result.items)}")

        print("\n" + "=" * 70)
        print("CAROUSEL ITEMS")
        print("=" * 70)

        image_count = 0
        video_count = 0
        supported_count = 0
        unsupported_count = 0

        for item in result.items:

            print(f"\nITEM {item.index}")
            print("-" * 50)

            print(f"Media type        : {item.media_type}")
            print(f"Download supported: {item.download_supported}")
            print(f"URL available     : {bool(item.url)}")

            if item.media_type == "image":

                image_count += 1

            elif item.media_type == "video":

                video_count += 1

            if item.download_supported:

                supported_count += 1

            else:

                unsupported_count += 1

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)

        print(f"Total items       : {len(result.items)}")
        print(f"Images            : {image_count}")
        print(f"Videos            : {video_count}")
        print(f"Supported items   : {supported_count}")
        print(f"Unsupported items : {unsupported_count}")

        print("\n" + "=" * 70)
        print("CLASSIFICATION")
        print("=" * 70)

        if image_count > 0 and video_count > 0:

            print("✅ MIXED CAROUSEL")

        elif image_count > 0:

            print("📷 IMAGE-ONLY CAROUSEL")

        elif video_count > 0:

            print("🎬 VIDEO-ONLY CAROUSEL")

        else:

            print("❓ UNKNOWN CAROUSEL")

        print("\n" + "=" * 70)
        print("V1 BEHAVIOR")
        print("=" * 70)

        if video_count > 0:

            print(
                "⚠️ Video items detected."
            )

            print(
                "Video downloading inside carousels "
                "will be implemented soon."
            )

            print(
                "✅ Supported images can still be "
                "previewed and downloaded."
            )

        else:

            print(
                "✅ All carousel items are currently "
                "supported."
            )

        print("=" * 70)

    except Exception as error:

        print("\n" + "=" * 70)
        print("❌ MIXED CAROUSEL TEST FAILED")
        print("=" * 70)

        print(f"\nError type : {type(error).__name__}")
        print(f"Error      : {error}")

        raise


if __name__ == "__main__":
    main()