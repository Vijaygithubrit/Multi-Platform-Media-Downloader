import yt_dlp

import src.detector as detector


class FakeYoutubeDL:
    def __init__(self, options, info=None, error=None):
        self.options = options
        self.info = info
        self.error = error

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def extract_info(self, url, download=False):
        if self.error:
            raise self.error

        return self.info


def test_detect_jpg_image():
    result = detector.detect_url(
        "https://example.com/photo.jpg"
    )

    assert result.media_type == "image"
    assert result.extension == "jpg"
    assert result.has_video is False
    assert result.has_audio is False


def test_detect_jpeg_normalizes_to_jpg():
    result = detector.detect_url(
        "https://example.com/photo.jpeg"
    )

    assert result.media_type == "image"
    assert result.extension == "jpg"


def test_detect_png_image():
    result = detector.detect_url(
        "https://example.com/photo.png"
    )

    assert result.media_type == "image"
    assert result.extension == "png"


def test_detect_webp_image():
    result = detector.detect_url(
        "https://example.com/photo.webp"
    )

    assert result.media_type == "image"
    assert result.extension == "webp"


def test_detect_image_with_query_parameters():
    result = detector.detect_url(
        "https://example.com/photo.jpg?width=1080&quality=90"
    )

    assert result.media_type == "image"
    assert result.extension == "jpg"


def test_detect_video_with_audio(monkeypatch):
    info = {
        "title": "Test Video",
        "duration": 120,
        "extractor_key": "YouTube",
        "formats": [
            {
                "vcodec": "avc1",
                "acodec": "none",
            },
            {
                "vcodec": "none",
                "acodec": "mp4a.40.2",
            },
        ],
    }

    monkeypatch.setattr(
        detector.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options,
            info=info,
        ),
    )

    result = detector.detect_url(
        "https://example.com/video"
    )

    assert result.media_type == "video"
    assert result.title == "Test Video"
    assert result.duration == 120
    assert result.extractor == "YouTube"
    assert result.has_video is True
    assert result.has_audio is True


def test_detect_video_only(monkeypatch):
    info = {
        "title": "Video Only",
        "duration": 60,
        "extractor_key": "TestExtractor",
        "formats": [
            {
                "vcodec": "avc1",
                "acodec": "none",
            }
        ],
    }

    monkeypatch.setattr(
        detector.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options,
            info=info,
        ),
    )

    result = detector.detect_url(
        "https://example.com/video-only"
    )

    assert result.media_type == "video"
    assert result.title == "Video Only"
    assert result.duration == 60
    assert result.extractor == "TestExtractor"
    assert result.has_video is True
    assert result.has_audio is False


def test_detect_audio_only(monkeypatch):
    info = {
        "title": "Test Audio",
        "duration": 180,
        "extractor": "TestAudioExtractor",
        "formats": [
            {
                "vcodec": "none",
                "acodec": "opus",
            }
        ],
    }

    monkeypatch.setattr(
        detector.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options,
            info=info,
        ),
    )

    result = detector.detect_url(
        "https://example.com/audio"
    )

    assert result.media_type == "audio"
    assert result.title == "Test Audio"
    assert result.duration == 180
    assert result.extractor == "TestAudioExtractor"
    assert result.has_video is False
    assert result.has_audio is True


def test_detect_video_from_direct_codecs(monkeypatch):
    info = {
        "title": "Direct Codec Video",
        "duration": 90,
        "extractor_key": "TestExtractor",
        "vcodec": "avc1",
        "acodec": "mp4a.40.2",
        "formats": [],
    }

    monkeypatch.setattr(
        detector.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options,
            info=info,
        ),
    )

    result = detector.detect_url(
        "https://example.com/video"
    )

    assert result.media_type == "video"
    assert result.has_video is True
    assert result.has_audio is True


def test_detect_unknown_media(monkeypatch):
    info = {
        "title": "Unknown Media",
        "duration": 30,
        "extractor_key": "TestExtractor",
        "formats": [],
    }

    monkeypatch.setattr(
        detector.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options,
            info=info,
        ),
    )

    result = detector.detect_url(
        "https://example.com/unknown"
    )

    assert result.media_type == "unknown"
    assert result.title == "Unknown Media"
    assert result.duration == 30
    assert result.extractor == "TestExtractor"
    assert result.has_video is False
    assert result.has_audio is False


def test_detect_empty_info(monkeypatch):
    monkeypatch.setattr(
        detector.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options,
            info=None,
        ),
    )

    result = detector.detect_url(
        "https://example.com/empty"
    )

    assert result.media_type == "unknown"
    assert result.reason == "No media information was returned."


def test_detect_ytdlp_download_error(monkeypatch):
    error = yt_dlp.utils.DownloadError(
        "Test download error"
    )

    monkeypatch.setattr(
        detector.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options,
            error=error,
        ),
    )

    result = detector.detect_url(
        "https://example.com/broken"
    )

    assert result.media_type == "unknown"
    assert "yt-dlp could not process this URL" in result.reason
    assert "Test download error" in result.reason


def test_detect_unexpected_error(monkeypatch):
    error = RuntimeError(
        "Unexpected test failure"
    )

    monkeypatch.setattr(
        detector.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options,
            error=error,
        ),
    )

    result = detector.detect_url(
        "https://example.com/error"
    )

    assert result.media_type == "unknown"
    assert "Unexpected detection error" in result.reason
    assert "Unexpected test failure" in result.reason