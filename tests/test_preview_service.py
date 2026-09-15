from pathlib import Path

import pytest

from src.services.preview_service import (
    PreviewResult,
    _get_extension_from_url,
    create_image_preview,
    delete_preview,
)


# --------------------------------------------------
# EXTENSION DETECTION
# --------------------------------------------------

def test_extension_from_jpg_url():

    url = (
        "https://example.com/photo.jpg"
    )

    assert (
        _get_extension_from_url(url)
        == "jpg"
    )


def test_extension_from_jpeg_url():

    url = (
        "https://example.com/photo.jpeg"
    )

    assert (
        _get_extension_from_url(url)
        == "jpg"
    )


def test_extension_from_webp_url():

    url = (
        "https://example.com/photo.webp"
    )

    assert (
        _get_extension_from_url(url)
        == "webp"
    )


def test_extension_from_unknown_url():

    url = (
        "https://example.com/photo"
    )

    assert (
        _get_extension_from_url(url)
        is None
    )


# --------------------------------------------------
# PREVIEW RESULT
# --------------------------------------------------

def test_preview_result():

    result = PreviewResult(
        path=Path(
            "temp/previews/preview_1.jpg"
        ),
        media_type="image",
        extension="jpg",
        size=12345,
    )

    assert result.media_type == "image"
    assert result.extension == "jpg"
    assert result.size == 12345
    assert result.path.name == "preview_1.jpg"


# --------------------------------------------------
# CREATE IMAGE PREVIEW
# --------------------------------------------------

def test_create_image_preview(monkeypatch):

    class FakeResponse:

        def __init__(self):

            self.headers = {
                "Content-Type": "image/jpeg"
            }

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):

            pass

        def read(self, size):

            if hasattr(
                self,
                "already_read",
            ):

                return b""

            self.already_read = True

            return b"fake image data"

    def fake_urlopen(
        request,
        timeout,
    ):

        assert timeout == 30

        return FakeResponse()

    monkeypatch.setattr(
        "src.services.preview_service.urlopen",
        fake_urlopen,
    )

    result = create_image_preview(
        "https://example.com/image.jpg"
    )

    try:

        assert result.media_type == "image"
        assert result.extension == "jpg"
        assert result.size > 0
        assert result.path.exists()
        assert result.path.parent.name == "previews"

    finally:

        if result.path.exists():

            result.path.unlink()


# --------------------------------------------------
# CREATE WEBP PREVIEW
# --------------------------------------------------

def test_create_webp_preview(monkeypatch):

    class FakeResponse:

        def __init__(self):

            self.headers = {
                "Content-Type": "image/webp"
            }

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):

            pass

        def read(self, size):

            if hasattr(
                self,
                "already_read",
            ):

                return b""

            self.already_read = True

            return b"webp data"

    def fake_urlopen(
        request,
        timeout,
    ):

        return FakeResponse()

    monkeypatch.setattr(
        "src.services.preview_service.urlopen",
        fake_urlopen,
    )

    result = create_image_preview(
        "https://example.com/image"
    )

    try:

        assert result.extension == "webp"
        assert result.path.suffix == ".webp"
        assert result.path.exists()

    finally:

        if result.path.exists():

            result.path.unlink()


# --------------------------------------------------
# DELETE PREVIEW
# --------------------------------------------------

def test_delete_preview(tmp_path):

    preview_path = (
        tmp_path / "preview.jpg"
    )

    preview_path.write_bytes(
        b"test"
    )

    result = PreviewResult(
        path=preview_path,
        media_type="image",
        extension="jpg",
        size=4,
    )

    assert preview_path.exists()

    delete_preview(result)

    assert not preview_path.exists()


# --------------------------------------------------
# DELETE PREVIEW BY PATH
# --------------------------------------------------

def test_delete_preview_by_path(tmp_path):

    preview_path = (
        tmp_path / "preview.jpg"
    )

    preview_path.write_bytes(
        b"test"
    )

    delete_preview(preview_path)

    assert not preview_path.exists()


# --------------------------------------------------
# INVALID IMAGE
# --------------------------------------------------

def test_invalid_image_content_type(
    monkeypatch,
):

    class FakeResponse:

        def __init__(self):

            self.headers = {
                "Content-Type": "text/html"
            }

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):

            pass

    def fake_urlopen(
        request,
        timeout,
    ):

        return FakeResponse()

    monkeypatch.setattr(
        "src.services.preview_service.urlopen",
        fake_urlopen,
    )

    with pytest.raises(RuntimeError):

        create_image_preview(
            "https://example.com/page"
        )


# --------------------------------------------------
# PREVIEW SIZE LIMIT
# --------------------------------------------------

def test_preview_size_limit(
    monkeypatch,
):

    class FakeResponse:

        def __init__(self):

            self.headers = {
                "Content-Type": "image/jpeg"
            }

        def __enter__(self):

            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):

            pass

        def read(self, size):

            return b"x" * 20

    def fake_urlopen(
        request,
        timeout,
    ):

        return FakeResponse()

    monkeypatch.setattr(
        "src.services.preview_service.urlopen",
        fake_urlopen,
    )

    with pytest.raises(RuntimeError):

        create_image_preview(
            "https://example.com/image.jpg",
            max_size=10,
        )