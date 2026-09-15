from pathlib import Path

import src.detector as detector
import src.image_downloader as image_downloader
import src.downloader as downloader

from src.validators import validate_url


class FakeYoutubeDL:
    def __init__(self, options, info):
        self.options = options
        self.info = info

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def extract_info(self, url, download=False):
        return self.info


def test_image_pipeline(
    tmp_path,
    monkeypatch,
):
    url = "https://example.com/photo.jpg"

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    valid, error = validate_url(url)

    assert valid is True
    assert not error

    # --------------------------------------------------
    # DETECTION
    # --------------------------------------------------

    result = detector.detect_url(url)

    assert result.media_type == "image"
    assert result.extension == "jpg"

    # --------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------

    output_path = tmp_path / "image1.jpg"

    monkeypatch.setattr(
        image_downloader,
        "download_image",
        lambda received_url: output_path,
    )

    downloaded = image_downloader.download_image(url)

    assert downloaded == output_path


def test_video_pipeline_to_video_download(
    monkeypatch,
):
    url = "https://example.com/video"

    video_info = {
        "title": "Integration Test Video",
        "duration": 120,
        "extractor_key": "TestExtractor",
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

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    valid, error = validate_url(url)

    assert valid is True
    assert not error

    # --------------------------------------------------
    # DETECTION
    # --------------------------------------------------

    monkeypatch.setattr(
        detector.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options,
            video_info,
        ),
    )

    result = detector.detect_url(url)

    assert result.media_type == "video"
    assert result.has_video is True
    assert result.has_audio is True

    # --------------------------------------------------
    # VIDEO DOWNLOAD
    # --------------------------------------------------

    expected_path = Path(
        "downloads/video1.mp4"
    )

    calls = []

    def fake_download_video(received_url):
        calls.append(received_url)
        return expected_path

    monkeypatch.setattr(
        downloader,
        "download_video",
        fake_download_video,
    )

    downloaded = downloader.download_video(url)

    assert downloaded == expected_path
    assert calls == [url]


def test_video_pipeline_to_audio_download(
    monkeypatch,
):
    url = "https://example.com/video"

    video_info = {
        "title": "Integration Test Video",
        "duration": 120,
        "extractor_key": "TestExtractor",
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

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    valid, error = validate_url(url)

    assert valid is True
    assert not error

    # --------------------------------------------------
    # DETECTION
    # --------------------------------------------------

    monkeypatch.setattr(
        detector.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options,
            video_info,
        ),
    )

    result = detector.detect_url(url)

    assert result.media_type == "video"
    assert result.has_video is True
    assert result.has_audio is True

    # --------------------------------------------------
    # AUDIO DOWNLOAD
    # --------------------------------------------------

    expected_path = Path(
        "downloads/audio1.mp3"
    )

    calls = []

    def fake_download_audio(received_url):
        calls.append(received_url)
        return expected_path

    monkeypatch.setattr(
        downloader,
        "download_audio",
        fake_download_audio,
    )

    downloaded = downloader.download_audio(url)

    assert downloaded == expected_path
    assert calls == [url]


def test_audio_pipeline(
    monkeypatch,
):
    url = "https://example.com/audio"

    audio_info = {
        "title": "Integration Test Audio",
        "duration": 180,
        "extractor": "TestAudioExtractor",
        "formats": [
            {
                "vcodec": "none",
                "acodec": "opus",
            }
        ],
    }

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    valid, error = validate_url(url)

    assert valid is True
    assert not error

    # --------------------------------------------------
    # DETECTION
    # --------------------------------------------------

    monkeypatch.setattr(
        detector.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options,
            audio_info,
        ),
    )

    result = detector.detect_url(url)

    assert result.media_type == "audio"
    assert result.has_video is False
    assert result.has_audio is True

    # --------------------------------------------------
    # AUDIO DOWNLOAD
    # --------------------------------------------------

    expected_path = Path(
        "downloads/audio1.mp3"
    )

    calls = []

    def fake_download_audio(received_url):
        calls.append(received_url)
        return expected_path

    monkeypatch.setattr(
        downloader,
        "download_audio",
        fake_download_audio,
    )

    downloaded = downloader.download_audio(url)

    assert downloaded == expected_path
    assert calls == [url]


def test_invalid_url_stops_before_detection(
    monkeypatch,
):
    url = "not-a-valid-url"

    detection_called = False

    def fake_detect_url(received_url):
        nonlocal detection_called
        detection_called = True
        return None

    monkeypatch.setattr(
        detector,
        "detect_url",
        fake_detect_url,
    )

    valid, error = validate_url(url)

    assert valid is False
    assert error is not None

    assert detection_called is False