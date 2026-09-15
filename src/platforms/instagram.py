import re
from dataclasses import dataclass
from pathlib import Path

import instaloader

from src.downloader import download_audio, download_video
from src.image_downloader import download_image


# --------------------------------------------------
# MEDIA ITEM
# --------------------------------------------------

@dataclass
class MediaItem:
    """
    Represents one media item inside an Instagram post.

    Examples:
        Item 1 -> image
        Item 2 -> image
        Item 3 -> video

    download_supported:
        True  -> currently supported by the application
        False -> detected correctly, but not supported yet
    """

    index: int
    media_type: str
    url: str | None = None
    download_supported: bool = True


# --------------------------------------------------
# INSTAGRAM POST RESULT
# --------------------------------------------------

@dataclass
class InstagramPostResult:
    """
    Represents an Instagram post.

    A post can contain:
        - one image
        - one video
        - multiple images/videos
    """

    shortcode: str
    post_type: str
    items: list[MediaItem]


# --------------------------------------------------
# SHORTCODE EXTRACTION
# --------------------------------------------------

def extract_shortcode(url: str) -> str:
    """
    Extract the shortcode from an Instagram post URL.

    Example:
        https://www.instagram.com/p/ABC123/

    Returns:
        ABC123
    """

    match = re.search(
        r"instagram\.com/(?:p|reel|tv)/([^/?#]+)",
        url,
        flags=re.IGNORECASE,
    )

    if not match:
        raise ValueError(
            "Could not extract Instagram post shortcode."
        )

    return match.group(1)


# --------------------------------------------------
# LOAD INSTAGRAM POST
# --------------------------------------------------

def load_instagram_post(url: str):
    """
    Load an Instagram post using Instaloader.

    This function only retrieves metadata.
    It does not download the media.
    """

    shortcode = extract_shortcode(url)

    loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
        quiet=True,
    )

    try:
        post = instaloader.Post.from_shortcode(
            loader.context,
            shortcode,
        )

    except Exception as error:
        raise RuntimeError(
            f"Could not load Instagram post:\n{error}"
        ) from error

    return post


# --------------------------------------------------
# EXTRACT POST MEDIA
# --------------------------------------------------

def extract_instagram_post(url: str) -> InstagramPostResult:
    """
    Extract media information from an Instagram post.

    Supported post types:

        GraphImage
        GraphVideo
        GraphSidecar

    For carousel posts:

        Images are currently supported.

        Videos are detected correctly but marked as
        unsupported until carousel video downloading
        is implemented.
    """

    post = load_instagram_post(url)

    items: list[MediaItem] = []

    # --------------------------------------------------
    # CAROUSEL
    # --------------------------------------------------

    if post.typename == "GraphSidecar":

        for index, node in enumerate(
            post.get_sidecar_nodes(),
            start=1,
        ):

            # ------------------------------------------
            # CAROUSEL VIDEO
            # ------------------------------------------

            if node.is_video:

                media_url = node.video_url
                media_type = "video"

                # Video carousel downloading is NOT
                # supported in V1.
                download_supported = False

            # ------------------------------------------
            # CAROUSEL IMAGE
            # ------------------------------------------

            else:

                media_url = node.display_url
                media_type = "image"

                # Image carousel downloading IS
                # supported in V1.
                download_supported = True

            if not media_url:
                raise RuntimeError(
                    f"Instagram carousel item {index} "
                    "does not have a downloadable URL."
                )

            items.append(
                MediaItem(
                    index=index,
                    media_type=media_type,
                    url=media_url,
                    download_supported=download_supported,
                )
            )

        return InstagramPostResult(
            shortcode=post.shortcode,
            post_type="carousel",
            items=items,
        )

    # --------------------------------------------------
    # SINGLE VIDEO
    # --------------------------------------------------

    if post.typename == "GraphVideo":

        if not post.video_url:
            raise RuntimeError(
                "Instagram video URL could not be obtained."
            )

        items.append(
            MediaItem(
                index=1,
                media_type="video",
                url=post.video_url,
                download_supported=True,
            )
        )

        return InstagramPostResult(
            shortcode=post.shortcode,
            post_type="single",
            items=items,
        )

    # --------------------------------------------------
    # SINGLE IMAGE
    # --------------------------------------------------

    if post.typename == "GraphImage":

        if not post.url:
            raise RuntimeError(
                "Instagram image URL could not be obtained."
            )

        items.append(
            MediaItem(
                index=1,
                media_type="image",
                url=post.url,
                download_supported=True,
            )
        )

        return InstagramPostResult(
            shortcode=post.shortcode,
            post_type="single",
            items=items,
        )

    # --------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------

    raise RuntimeError(
        f"Unsupported Instagram post type: {post.typename}"
    )


# --------------------------------------------------
# DOWNLOAD ONE INSTAGRAM ITEM
# --------------------------------------------------

def download_instagram_item(
    item: MediaItem,
    choice: str | None = None,
) -> Path:
    """
    Download one Instagram media item.

    Image:
        Downloads automatically.

    Single Video:
        Requires a choice:
            "video"
            "audio"

    Carousel Video:
        Currently unsupported.
    """

    if not item.url:
        raise ValueError(
            f"Instagram item {item.index} "
            "does not have a media URL."
        )

    # --------------------------------------------------
    # UNSUPPORTED ITEM
    # --------------------------------------------------

    if not item.download_supported:
        raise RuntimeError(
            f"Instagram carousel item {item.index} "
            f"is a {item.media_type}.\n"
            "Carousel video downloading will be "
            "implemented soon."
        )

    # --------------------------------------------------
    # IMAGE
    # --------------------------------------------------

    if item.media_type == "image":

        return download_image(item.url)

    # --------------------------------------------------
    # VIDEO
    # --------------------------------------------------

    if item.media_type == "video":

        if choice is None:
            raise ValueError(
                "A download choice is required for "
                "Instagram video: 'video' or 'audio'."
            )

        choice = choice.lower().strip()

        if choice == "video":

            return download_video(item.url)

        if choice == "audio":

            return download_audio(item.url)

        raise ValueError(
            "Invalid Instagram video choice. "
            "Use 'video' or 'audio'."
        )

    # --------------------------------------------------
    # UNKNOWN MEDIA TYPE
    # --------------------------------------------------

    raise RuntimeError(
        f"Unsupported Instagram media type: "
        f"{item.media_type}"
    )


# --------------------------------------------------
# DOWNLOAD MULTIPLE INSTAGRAM ITEMS
# --------------------------------------------------

def download_instagram_items(
    result: InstagramPostResult,
    selected_indices: list[int] | None = None,
    choice: str | None = None,
) -> list[Path]:
    """
    Download multiple Instagram post items.

    For carousel posts:

        - Supported images are downloaded.
        - Unsupported carousel videos are skipped.
        - Single videos remain fully supported.

    Parameters:
        result:
            InstagramPostResult containing the media items.

        selected_indices:
            None:
                Download all supported items.

            Example:
                [1, 3, 5]
                Download only items 1, 3 and 5.

        choice:
            Used for supported video items.

            "video":
                Download video.

            "audio":
                Extract audio.

    Returns:
        List of successfully downloaded file paths.
    """

    # --------------------------------------------------
    # CHECK RESULT
    # --------------------------------------------------

    if not result.items:

        raise ValueError(
            "Instagram post contains no media items."
        )

    # --------------------------------------------------
    # DETERMINE ITEMS TO DOWNLOAD
    # --------------------------------------------------

    if selected_indices is None:

        items_to_download = [
            item
            for item in result.items
            if item.download_supported
        ]

    else:

        if not selected_indices:

            raise ValueError(
                "No Instagram items were selected."
            )

        available_indices = {
            item.index
            for item in result.items
        }

        invalid_indices = [
            index
            for index in selected_indices
            if index not in available_indices
        ]

        if invalid_indices:

            raise ValueError(
                "Invalid Instagram item index: "
                f"{invalid_indices}"
            )

        items_by_index = {
            item.index: item
            for item in result.items
        }

        items_to_download = [
            items_by_index[index]
            for index in selected_indices
            if items_by_index[index].download_supported
        ]

    # --------------------------------------------------
    # CHECK SUPPORTED ITEMS
    # --------------------------------------------------

    if not items_to_download:

        raise ValueError(
            "No supported Instagram media items "
            "were selected."
        )

    # --------------------------------------------------
    # DOWNLOAD ITEMS
    # --------------------------------------------------

    downloaded_files: list[Path] = []

    for item in items_to_download:

        output_path = download_instagram_item(
            item,
            choice=choice,
        )

        downloaded_files.append(
            output_path
        )

    # --------------------------------------------------
    # RETURN RESULTS
    # --------------------------------------------------

    return downloaded_files