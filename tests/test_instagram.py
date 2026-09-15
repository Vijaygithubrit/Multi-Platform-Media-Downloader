from pathlib import Path
from src.platforms.instagram import (
    InstagramPostResult,
    MediaItem,
    download_instagram_item,
    download_instagram_items,
    extract_shortcode,
)
from src.services.carousel_service import CarouselSession
import pytest
from src.services.preview_service import (
    PreviewResult,
)

from src.platforms.instagram import (
    MediaItem,
    download_instagram_item,
    extract_shortcode,
)


# --------------------------------------------------
# SHORTCODE TESTS
# --------------------------------------------------

def test_extract_instagram_shortcode():

    url = (
        "https://www.instagram.com/p/"
        "Dc_XgIoE0Wt/"
        "?utm_source=ig_web_copy_link"
    )

    assert extract_shortcode(url) == "Dc_XgIoE0Wt"


def test_extract_instagram_shortcode_with_query():

    url = (
        "https://www.instagram.com/p/"
        "ABC123xyz/"
        "?some_parameter=value"
    )

    assert extract_shortcode(url) == "ABC123xyz"


def test_extract_instagram_shortcode_invalid_url():

    url = "https://www.youtube.com/watch?v=123"

    with pytest.raises(ValueError):

        extract_shortcode(url)


# --------------------------------------------------
# MEDIA ITEM TESTS
# --------------------------------------------------

def test_image_item():

    item = MediaItem(
        index=1,
        media_type="image",
        url="https://example.com/image.jpg",
    )

    assert item.index == 1
    assert item.media_type == "image"
    assert item.url.endswith("image.jpg")


def test_video_item():

    item = MediaItem(
        index=2,
        media_type="video",
        url="https://example.com/video.mp4",
    )

    assert item.index == 2
    assert item.media_type == "video"
    assert item.url.endswith("video.mp4")


# --------------------------------------------------
# DOWNLOAD IMAGE
# --------------------------------------------------

def test_download_image_item(monkeypatch):

    expected_path = Path(
        "downloads/image1.jpg"
    )

    def fake_download_image(url):

        assert url == "https://example.com/image.jpg"

        return expected_path

    monkeypatch.setattr(
        "src.platforms.instagram.download_image",
        fake_download_image,
    )

    item = MediaItem(
        index=1,
        media_type="image",
        url="https://example.com/image.jpg",
    )

    result = download_instagram_item(item)

    assert result == expected_path


# --------------------------------------------------
# DOWNLOAD VIDEO
# --------------------------------------------------

def test_download_video_item(monkeypatch):

    expected_path = Path(
        "downloads/video1.mp4"
    )

    def fake_download_video(url):

        assert url == "https://example.com/video.mp4"

        return expected_path

    monkeypatch.setattr(
        "src.platforms.instagram.download_video",
        fake_download_video,
    )

    item = MediaItem(
        index=2,
        media_type="video",
        url="https://example.com/video.mp4",
    )

    result = download_instagram_item(
        item,
        choice="video",
    )

    assert result == expected_path


# --------------------------------------------------
# DOWNLOAD VIDEO AS AUDIO
# --------------------------------------------------

def test_download_video_item_as_audio(monkeypatch):

    expected_path = Path(
        "downloads/audio1.mp3"
    )

    def fake_download_audio(url):

        assert url == "https://example.com/video.mp4"

        return expected_path

    monkeypatch.setattr(
        "src.platforms.instagram.download_audio",
        fake_download_audio,
    )

    item = MediaItem(
        index=3,
        media_type="video",
        url="https://example.com/video.mp4",
    )

    result = download_instagram_item(
        item,
        choice="audio",
    )

    assert result == expected_path


# --------------------------------------------------
# VIDEO REQUIRES CHOICE
# --------------------------------------------------

def test_video_requires_choice():

    item = MediaItem(
        index=1,
        media_type="video",
        url="https://example.com/video.mp4",
    )

    with pytest.raises(ValueError):

        download_instagram_item(item)


# --------------------------------------------------
# VIDEO CHOICE NORMALIZATION
# --------------------------------------------------

def test_video_choice_is_case_insensitive(monkeypatch):

    expected_path = Path(
        "downloads/video2.mp4"
    )

    def fake_download_video(url):

        return expected_path

    monkeypatch.setattr(
        "src.platforms.instagram.download_video",
        fake_download_video,
    )

    item = MediaItem(
        index=1,
        media_type="video",
        url="https://example.com/video.mp4",
    )

    result = download_instagram_item(
        item,
        choice="  VIDEO  ",
    )

    assert result == expected_path


# --------------------------------------------------
# INVALID VIDEO CHOICE
# --------------------------------------------------

def test_invalid_video_choice():

    item = MediaItem(
        index=1,
        media_type="video",
        url="https://example.com/video.mp4",
    )

    with pytest.raises(ValueError):

        download_instagram_item(
            item,
            choice="document",
        )


# --------------------------------------------------
# MISSING URL
# --------------------------------------------------

def test_missing_media_url():

    item = MediaItem(
        index=1,
        media_type="image",
        url=None,
    )

    with pytest.raises(ValueError):

        download_instagram_item(item)


# --------------------------------------------------
# UNKNOWN MEDIA TYPE
# --------------------------------------------------

def test_unknown_media_type():

    item = MediaItem(
        index=1,
        media_type="unknown",
        url="https://example.com/file",
    )

    with pytest.raises(RuntimeError):

        download_instagram_item(item)
        # --------------------------------------------------
# BATCH DOWNLOAD - ALL ITEMS
# --------------------------------------------------

def test_download_all_instagram_items(monkeypatch):

    result = InstagramPostResult(
        shortcode="ABC123",
        post_type="carousel",
        items=[
            MediaItem(
                index=1,
                media_type="image",
                url="https://example.com/image1.jpg",
            ),
            MediaItem(
                index=2,
                media_type="image",
                url="https://example.com/image2.jpg",
            ),
            MediaItem(
                index=3,
                media_type="image",
                url="https://example.com/image3.jpg",
            ),
        ],
    )

    downloaded = []

    def fake_download(item, choice=None):

        downloaded.append(
            (item.index, choice)
        )

        return Path(
            f"downloads/image{item.index}.jpg"
        )

    monkeypatch.setattr(
        "src.platforms.instagram.download_instagram_item",
        fake_download,
    )

    files = download_instagram_items(
        result
    )

    assert downloaded == [
        (1, None),
        (2, None),
        (3, None),
    ]

    assert files == [
        Path("downloads/image1.jpg"),
        Path("downloads/image2.jpg"),
        Path("downloads/image3.jpg"),
    ]


# --------------------------------------------------
# BATCH DOWNLOAD - SELECTED ITEMS
# --------------------------------------------------

def test_download_selected_instagram_items(monkeypatch):

    result = InstagramPostResult(
        shortcode="ABC123",
        post_type="carousel",
        items=[
            MediaItem(
                index=1,
                media_type="image",
                url="https://example.com/image1.jpg",
            ),
            MediaItem(
                index=2,
                media_type="image",
                url="https://example.com/image2.jpg",
            ),
            MediaItem(
                index=3,
                media_type="image",
                url="https://example.com/image3.jpg",
            ),
            MediaItem(
                index=4,
                media_type="image",
                url="https://example.com/image4.jpg",
            ),
            MediaItem(
                index=5,
                media_type="image",
                url="https://example.com/image5.jpg",
            ),
        ],
    )

    downloaded = []

    def fake_download(item, choice=None):

        downloaded.append(item.index)

        return Path(
            f"downloads/image{item.index}.jpg"
        )

    monkeypatch.setattr(
        "src.platforms.instagram.download_instagram_item",
        fake_download,
    )

    files = download_instagram_items(
        result,
        selected_indices=[1, 3, 5],
    )

    assert downloaded == [1, 3, 5]

    assert files == [
        Path("downloads/image1.jpg"),
        Path("downloads/image3.jpg"),
        Path("downloads/image5.jpg"),
    ]


# --------------------------------------------------
# SELECTED ITEMS PRESERVE USER ORDER
# --------------------------------------------------

def test_selected_items_preserve_requested_order(monkeypatch):

    result = InstagramPostResult(
        shortcode="ABC123",
        post_type="carousel",
        items=[
            MediaItem(
                index=1,
                media_type="image",
                url="https://example.com/image1.jpg",
            ),
            MediaItem(
                index=2,
                media_type="image",
                url="https://example.com/image2.jpg",
            ),
            MediaItem(
                index=3,
                media_type="image",
                url="https://example.com/image3.jpg",
            ),
        ],
    )

    downloaded = []

    def fake_download(item, choice=None):

        downloaded.append(item.index)

        return Path(
            f"downloads/image{item.index}.jpg"
        )

    monkeypatch.setattr(
        "src.platforms.instagram.download_instagram_item",
        fake_download,
    )

    download_instagram_items(
        result,
        selected_indices=[3, 1],
    )

    assert downloaded == [3, 1]


# --------------------------------------------------
# EMPTY SELECTION
# --------------------------------------------------

def test_empty_selected_indices():

    result = InstagramPostResult(
        shortcode="ABC123",
        post_type="carousel",
        items=[
            MediaItem(
                index=1,
                media_type="image",
                url="https://example.com/image.jpg",
            ),
        ],
    )

    with pytest.raises(ValueError):

        download_instagram_items(
            result,
            selected_indices=[],
        )


# --------------------------------------------------
# INVALID SELECTION
# --------------------------------------------------

def test_invalid_selected_index():

    result = InstagramPostResult(
        shortcode="ABC123",
        post_type="carousel",
        items=[
            MediaItem(
                index=1,
                media_type="image",
                url="https://example.com/image.jpg",
            ),
            MediaItem(
                index=2,
                media_type="image",
                url="https://example.com/image2.jpg",
            ),
        ],
    )

    with pytest.raises(ValueError):

        download_instagram_items(
            result,
            selected_indices=[1, 5],
        )


# --------------------------------------------------
# VIDEO CHOICE IS PASSED TO EACH ITEM
# --------------------------------------------------

def test_batch_video_choice(monkeypatch):

    result = InstagramPostResult(
        shortcode="ABC123",
        post_type="carousel",
        items=[
            MediaItem(
                index=1,
                media_type="video",
                url="https://example.com/video1.mp4",
            ),
            MediaItem(
                index=2,
                media_type="video",
                url="https://example.com/video2.mp4",
            ),
        ],
    )

    choices = []

    def fake_download(item, choice=None):

        choices.append(
            (item.index, choice)
        )

        return Path(
            f"downloads/video{item.index}.mp4"
        )

    monkeypatch.setattr(
        "src.platforms.instagram.download_instagram_item",
        fake_download,
    )

    download_instagram_items(
        result,
        choice="video",
    )

    assert choices == [
        (1, "video"),
        (2, "video"),
    ]


# --------------------------------------------------
# EMPTY POST
# --------------------------------------------------

def test_batch_download_empty_post():

    result = InstagramPostResult(
        shortcode="ABC123",
        post_type="carousel",
        items=[],
    )

    with pytest.raises(ValueError):

        download_instagram_items(result)
        # --------------------------------------------------
# CAROUSEL SESSION FIXTURE
# --------------------------------------------------

def create_test_carousel():

    return InstagramPostResult(
        shortcode="ABC123",
        post_type="carousel",
        items=[
            MediaItem(
                index=1,
                media_type="image",
                url="https://example.com/image1.jpg",
            ),
            MediaItem(
                index=2,
                media_type="image",
                url="https://example.com/image2.jpg",
            ),
            MediaItem(
                index=3,
                media_type="image",
                url="https://example.com/image3.jpg",
            ),
            MediaItem(
                index=4,
                media_type="image",
                url="https://example.com/image4.jpg",
            ),
            MediaItem(
                index=5,
                media_type="image",
                url="https://example.com/image5.jpg",
            ),
        ],
    )


# --------------------------------------------------
# SESSION INITIAL STATE
# --------------------------------------------------

def test_carousel_session_initial_state():

    session = CarouselSession(
        create_test_carousel()
    )

    assert session.total_items == 5
    assert session.downloaded_count == 0
    assert len(session.remaining_items) == 5
    assert session.is_complete is False


# --------------------------------------------------
# GET ITEM
# --------------------------------------------------

def test_carousel_session_get_item():

    session = CarouselSession(
        create_test_carousel()
    )

    item = session.get_item(3)

    assert item.index == 3
    assert item.media_type == "image"


# --------------------------------------------------
# INVALID ITEM
# --------------------------------------------------

def test_carousel_session_get_invalid_item():

    session = CarouselSession(
        create_test_carousel()
    )

    with pytest.raises(ValueError):

        session.get_item(10)


# --------------------------------------------------
# DOWNLOAD SELECTED
# --------------------------------------------------

def test_session_download_selected(monkeypatch):

    session = CarouselSession(
        create_test_carousel()
    )

    downloaded = []

    def fake_download(item, choice=None):

        downloaded.append(
            (item.index, choice)
        )

        return Path(
            f"downloads/image{item.index}.jpg"
        )

    monkeypatch.setattr(
        "src.services.carousel_service.download_instagram_item",
        fake_download,
    )

    files = session.download_selected(
        [1, 3],
    )

    assert downloaded == [
        (1, None),
        (3, None),
    ]

    assert len(files) == 2

    assert session.downloaded_indices == {
        1,
        3,
    }

    assert [
        item.index
        for item in session.remaining_items
    ] == [
        2,
        4,
        5,
    ]


# --------------------------------------------------
# DOWNLOAD REMAINING
# --------------------------------------------------

def test_session_download_remaining(monkeypatch):

    session = CarouselSession(
        create_test_carousel()
    )

    downloaded = []

    def fake_download(item, choice=None):

        downloaded.append(item.index)

        return Path(
            f"downloads/image{item.index}.jpg"
        )

    monkeypatch.setattr(
        "src.services.carousel_service.download_instagram_item",
        fake_download,
    )

    session.download_selected(
        [1, 3]
    )

    files = session.download_remaining()

    assert downloaded == [
        1,
        3,
        2,
        4,
        5,
    ]

    assert len(files) == 3

    assert session.is_complete is True

    assert session.remaining_items == []


# --------------------------------------------------
# DOWNLOAD ALL
# --------------------------------------------------

def test_session_download_all(monkeypatch):

    session = CarouselSession(
        create_test_carousel()
    )

    downloaded = []

    def fake_download(item, choice=None):

        downloaded.append(item.index)

        return Path(
            f"downloads/image{item.index}.jpg"
        )

    monkeypatch.setattr(
        "src.services.carousel_service.download_instagram_item",
        fake_download,
    )

    files = session.download_all()

    assert downloaded == [
        1,
        2,
        3,
        4,
        5,
    ]

    assert len(files) == 5

    assert session.is_complete is True


# --------------------------------------------------
# DOWNLOAD ALL AFTER SOME ITEMS
# --------------------------------------------------

def test_session_download_all_only_downloads_remaining(
    monkeypatch,
):

    session = CarouselSession(
        create_test_carousel()
    )

    downloaded = []

    def fake_download(item, choice=None):

        downloaded.append(item.index)

        return Path(
            f"downloads/image{item.index}.jpg"
        )

    monkeypatch.setattr(
        "src.services.carousel_service.download_instagram_item",
        fake_download,
    )

    session.download_selected(
        [2, 4]
    )

    downloaded.clear()

    session.download_all()

    assert downloaded == [
        1,
        3,
        5,
    ]


# --------------------------------------------------
# DUPLICATE SELECTION
# --------------------------------------------------

def test_session_rejects_duplicate_selection():

    session = CarouselSession(
        create_test_carousel()
    )

    with pytest.raises(ValueError):

        session.download_selected(
            [1, 1, 3]
        )


# --------------------------------------------------
# INVALID SELECTION
# --------------------------------------------------

def test_session_rejects_invalid_selection():

    session = CarouselSession(
        create_test_carousel()
    )

    with pytest.raises(ValueError):

        session.download_selected(
            [1, 7]
        )


# --------------------------------------------------
# EMPTY SELECTION
# --------------------------------------------------

def test_session_rejects_empty_selection():

    session = CarouselSession(
        create_test_carousel()
    )

    with pytest.raises(ValueError):

        session.download_selected([])


# --------------------------------------------------
# ALREADY DOWNLOADED ITEM
# --------------------------------------------------

def test_session_rejects_already_downloaded_item(
    monkeypatch,
):

    session = CarouselSession(
        create_test_carousel()
    )

    def fake_download(item, choice=None):

        return Path(
            f"downloads/image{item.index}.jpg"
        )

    monkeypatch.setattr(
        "src.services.carousel_service.download_instagram_item",
        fake_download,
    )

    session.download_selected([1])

    with pytest.raises(ValueError):

        session.download_selected([1])


# --------------------------------------------------
# STATUS
# --------------------------------------------------

def test_session_status(monkeypatch):

    session = CarouselSession(
        create_test_carousel()
    )

    def fake_download(item, choice=None):

        return Path(
            f"downloads/image{item.index}.jpg"
        )

    monkeypatch.setattr(
        "src.services.carousel_service.download_instagram_item",
        fake_download,
    )

    session.download_selected(
        [1, 3]
    )

    status = session.status()

    assert status == {
        "total": 5,
        "downloaded": 2,
        "remaining": 3,
        "downloaded_indices": [1, 3],
        "remaining_indices": [2, 4, 5],
        "unsupported_indices": [],
    }


# --------------------------------------------------
# COMPLETE SESSION
# --------------------------------------------------

def test_session_completion(monkeypatch):

    session = CarouselSession(
        create_test_carousel()
    )

    def fake_download(item, choice=None):

        return Path(
            f"downloads/image{item.index}.jpg"
        )

    monkeypatch.setattr(
        "src.services.carousel_service.download_instagram_item",
        fake_download,
    )

    session.download_all()

    assert session.is_complete is True

    with pytest.raises(ValueError):

        session.download_remaining()
        # --------------------------------------------------
# SESSION IMAGE PREVIEW
# --------------------------------------------------

def test_session_preview_image(monkeypatch):

    session = CarouselSession(
        create_test_carousel()
    )

    expected_preview = PreviewResult(
        path=Path(
            "temp/previews/preview_test.jpg"
        ),
        media_type="image",
        extension="jpg",
        size=12345,
    )

    captured_urls = []

    def fake_create_image_preview(url):

        captured_urls.append(url)

        return expected_preview

    monkeypatch.setattr(
        "src.services.carousel_service.create_image_preview",
        fake_create_image_preview,
    )

    preview = session.preview_item(1)

    assert preview is expected_preview

    assert captured_urls == [
        "https://example.com/image1.jpg"
    ]

    # Previewing must NOT mark the item
    # as downloaded.

    assert session.downloaded_indices == set()

    assert session.downloaded_count == 0

    assert len(session.remaining_items) == 5


# --------------------------------------------------
# SESSION PREVIEW DIFFERENT ITEM
# --------------------------------------------------

def test_session_preview_selected_item(
    monkeypatch,
):

    session = CarouselSession(
        create_test_carousel()
    )

    captured_urls = []

    def fake_create_image_preview(url):

        captured_urls.append(url)

        return PreviewResult(
            path=Path(
                "temp/previews/preview_test.jpg"
            ),
            media_type="image",
            extension="jpg",
            size=100,
        )

    monkeypatch.setattr(
        "src.services.carousel_service.create_image_preview",
        fake_create_image_preview,
    )

    session.preview_item(4)

    assert captured_urls == [
        "https://example.com/image4.jpg"
    ]


# --------------------------------------------------
# SESSION PREVIEW INVALID ITEM
# --------------------------------------------------

def test_session_preview_invalid_item():

    session = CarouselSession(
        create_test_carousel()
    )

    with pytest.raises(ValueError):

        session.preview_item(10)


# --------------------------------------------------
# SESSION PREVIEW WITHOUT URL
# --------------------------------------------------

def test_session_preview_without_url():

    result = InstagramPostResult(
        shortcode="ABC123",
        post_type="carousel",
        items=[
            MediaItem(
                index=1,
                media_type="image",
                url=None,
            ),
        ],
    )

    session = CarouselSession(result)

    with pytest.raises(RuntimeError):

        session.preview_item(1)


# --------------------------------------------------
# SESSION IMAGE PREVIEW DOES NOT DOWNLOAD
# --------------------------------------------------

def test_preview_does_not_change_session_status(
    monkeypatch,
):

    session = CarouselSession(
        create_test_carousel()
    )

    def fake_create_image_preview(url):

        return PreviewResult(
            path=Path(
                "temp/previews/preview_test.jpg"
            ),
            media_type="image",
            extension="jpg",
            size=100,
        )

    monkeypatch.setattr(
        "src.services.carousel_service.create_image_preview",
        fake_create_image_preview,
    )

    before = session.status()

    session.preview_item(3)

    after = session.status()

    assert before == after