from pathlib import Path

import pytest

import src.media_service as media_service
from src.detector import DetectionResult


# ============================================================
# HELPERS
# ============================================================


def make_image_result():
    return DetectionResult(
        media_type="image",
        reason="Test image detected.",
        extension="jpg",
        has_video=False,
        has_audio=False,
    )


def make_video_result(has_audio=True):
    return DetectionResult(
        media_type="video",
        reason="Test video detected.",
        extension=None,
        has_video=True,
        has_audio=has_audio,
    )


def make_audio_result():
    return DetectionResult(
        media_type="audio",
        reason="Test audio detected.",
        extension=None,
        has_video=False,
        has_audio=True,
    )


def make_unknown_result():
    return DetectionResult(
        media_type="unknown",
        reason="Unsupported test media.",
        extension=None,
        has_video=False,
        has_audio=False,
    )


# ============================================================
# detect_media() TESTS
# ============================================================


def test_detect_media_valid_image(
    monkeypatch,
):
    url = "https://example.com/image.jpg"

    expected_result = make_image_result()

    monkeypatch.setattr(
        media_service,
        "validate_url",
        lambda received_url: (True, ""),
    )

    monkeypatch.setattr(
        media_service,
        "detect_url",
        lambda received_url: expected_result,
    )

    result = media_service.detect_media(url)

    assert result is expected_result
    assert result.media_type == "image"


def test_detect_media_valid_video(
    monkeypatch,
):
    url = "https://example.com/video"

    expected_result = make_video_result()

    monkeypatch.setattr(
        media_service,
        "validate_url",
        lambda received_url: (True, ""),
    )

    monkeypatch.setattr(
        media_service,
        "detect_url",
        lambda received_url: expected_result,
    )

    result = media_service.detect_media(url)

    assert result is expected_result
    assert result.media_type == "video"


def test_detect_media_valid_audio(
    monkeypatch,
):
    url = "https://example.com/audio"

    expected_result = make_audio_result()

    monkeypatch.setattr(
        media_service,
        "validate_url",
        lambda received_url: (True, ""),
    )

    monkeypatch.setattr(
        media_service,
        "detect_url",
        lambda received_url: expected_result,
    )

    result = media_service.detect_media(url)

    assert result is expected_result
    assert result.media_type == "audio"


def test_detect_media_rejects_invalid_url(
    monkeypatch,
):
    url = "not-a-valid-url"

    monkeypatch.setattr(
        media_service,
        "validate_url",
        lambda received_url: (
            False,
            "Invalid URL format.",
        ),
    )

    with pytest.raises(
        ValueError,
        match="Invalid URL",
    ):
        media_service.detect_media(url)


def test_detect_media_rejects_unknown_media(
    monkeypatch,
):
    url = "https://example.com/unknown"

    unknown_result = make_unknown_result()

    monkeypatch.setattr(
        media_service,
        "validate_url",
        lambda received_url: (True, ""),
    )

    monkeypatch.setattr(
        media_service,
        "detect_url",
        lambda received_url: unknown_result,
    )

    with pytest.raises(
        RuntimeError,
        match="Unsupported or unknown media",
    ):
        media_service.detect_media(url)


# ============================================================
# download_media() IMAGE TESTS
# ============================================================


def test_download_media_image(
    monkeypatch,
):
    url = "https://example.com/image.jpg"

    expected_path = Path(
        "downloads/image1.jpg"
    )

    calls = []

    def fake_download_image(received_url):
        calls.append(received_url)
        return expected_path

    monkeypatch.setattr(
        media_service,
        "download_image",
        fake_download_image,
    )

    result = media_service.download_media(
        url,
        make_image_result(),
    )

    assert result == expected_path
    assert calls == [url]


# ============================================================
# download_media() AUDIO TESTS
# ============================================================


def test_download_media_audio(
    monkeypatch,
):
    url = "https://example.com/audio"

    expected_path = Path(
        "downloads/audio1.mp3"
    )

    calls = []

    def fake_download_audio(received_url):
        calls.append(received_url)
        return expected_path

    monkeypatch.setattr(
        media_service,
        "download_audio",
        fake_download_audio,
    )

    result = media_service.download_media(
        url,
        make_audio_result(),
    )

    assert result == expected_path
    assert calls == [url]


# ============================================================
# download_media() VIDEO TESTS
# ============================================================


def test_download_media_video_requires_choice():
    url = "https://example.com/video"

    with pytest.raises(
        ValueError,
        match="choice is required",
    ):
        media_service.download_media(
            url,
            make_video_result(),
        )


def test_download_media_video_choice(
    monkeypatch,
):
    url = "https://example.com/video"

    expected_path = Path(
        "downloads/video1.mp4"
    )

    calls = []

    def fake_download_video(received_url):
        calls.append(received_url)
        return expected_path

    monkeypatch.setattr(
        media_service,
        "download_video",
        fake_download_video,
    )

    result = media_service.download_media(
        url,
        make_video_result(),
        "video",
    )

    assert result == expected_path
    assert calls == [url]


def test_download_media_video_audio_choice(
    monkeypatch,
):
    url = "https://example.com/video"

    expected_path = Path(
        "downloads/audio1.mp3"
    )

    calls = []

    def fake_download_audio(received_url):
        calls.append(received_url)
        return expected_path

    monkeypatch.setattr(
        media_service,
        "download_audio",
        fake_download_audio,
    )

    result = media_service.download_media(
        url,
        make_video_result(),
        "audio",
    )

    assert result == expected_path
    assert calls == [url]


def test_download_media_video_choice_is_case_insensitive(
    monkeypatch,
):
    url = "https://example.com/video"

    expected_path = Path(
        "downloads/video1.mp4"
    )

    monkeypatch.setattr(
        media_service,
        "download_video",
        lambda received_url: expected_path,
    )

    result = media_service.download_media(
        url,
        make_video_result(),
        "  VIDEO  ",
    )

    assert result == expected_path


def test_download_media_rejects_invalid_video_choice():
    url = "https://example.com/video"

    with pytest.raises(
        ValueError,
        match="Invalid video download choice",
    ):
        media_service.download_media(
            url,
            make_video_result(),
            "document",
        )


# ============================================================
# download_media() UNKNOWN TEST
# ============================================================


def test_download_media_rejects_unknown_media_type():
    url = "https://example.com/unknown"

    with pytest.raises(
        RuntimeError,
        match="Unsupported media type",
    ):
        media_service.download_media(
            url,
            make_unknown_result(),
        )


# ============================================================
# process_url() TESTS
# ============================================================


def test_process_url_image(
    monkeypatch,
):
    url = "https://example.com/image.jpg"

    expected_result = make_image_result()
    expected_path = Path(
        "downloads/image1.jpg"
    )

    monkeypatch.setattr(
        media_service,
        "detect_media",
        lambda received_url: expected_result,
    )

    monkeypatch.setattr(
        media_service,
        "download_media",
        lambda received_url, result, choice=None:
            expected_path,
    )

    result = media_service.process_url(url)

    assert result == expected_path


def test_process_url_video(
    monkeypatch,
):
    url = "https://example.com/video"

    expected_result = make_video_result()
    expected_path = Path(
        "downloads/video1.mp4"
    )

    captured = {}

    monkeypatch.setattr(
        media_service,
        "detect_media",
        lambda received_url: expected_result,
    )

    def fake_download_media(
        received_url,
        result,
        choice=None,
    ):
        captured["url"] = received_url
        captured["result"] = result
        captured["choice"] = choice

        return expected_path

    monkeypatch.setattr(
        media_service,
        "download_media",
        fake_download_media,
    )

    result = media_service.process_url(
        url,
        "video",
    )

    assert result == expected_path
    assert captured["url"] == url
    assert captured["result"] is expected_result
    assert captured["choice"] == "video"


def test_process_url_audio_choice(
    monkeypatch,
):
    url = "https://example.com/video"

    expected_result = make_video_result()
    expected_path = Path(
        "downloads/audio1.mp3"
    )

    captured = {}

    monkeypatch.setattr(
        media_service,
        "detect_media",
        lambda received_url: expected_result,
    )

    def fake_download_media(
        received_url,
        result,
        choice=None,
    ):
        captured["url"] = received_url
        captured["result"] = result
        captured["choice"] = choice

        return expected_path

    monkeypatch.setattr(
        media_service,
        "download_media",
        fake_download_media,
    )

    result = media_service.process_url(
        url,
        "audio",
    )

    assert result == expected_path
    assert captured["url"] == url
    assert captured["result"] is expected_result
    assert captured["choice"] == "audio"