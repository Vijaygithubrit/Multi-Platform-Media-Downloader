from pathlib import Path
from types import SimpleNamespace

import pytest

import src.image_downloader as image_downloader


class FakeHeaders:
    def __init__(self, content_type):
        self.content_type = content_type

    def get_content_type(self):
        return self.content_type


class FakeResponse:
    def __init__(self, data, content_type):
        self.data = data
        self.position = 0
        self.headers = FakeHeaders(content_type)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self, size=-1):
        if self.position >= len(self.data):
            return b""

        if size == -1:
            chunk = self.data[self.position:]
            self.position = len(self.data)
            return chunk

        chunk = self.data[
            self.position:self.position + size
        ]

        self.position += len(chunk)

        return chunk


def test_get_extension_from_jpg_url():
    result = image_downloader._get_extension_from_url(
        "https://example.com/photo.jpg"
    )

    assert result == "jpg"


def test_get_extension_from_jpeg_url():
    result = image_downloader._get_extension_from_url(
        "https://example.com/photo.jpeg"
    )

    assert result == "jpg"


def test_get_extension_from_tif_url():
    result = image_downloader._get_extension_from_url(
        "https://example.com/photo.tif"
    )

    assert result == "tif"


def test_get_extension_from_url_with_query():
    result = image_downloader._get_extension_from_url(
        "https://example.com/photo.webp?width=1000"
    )

    assert result == "webp"


def test_get_extension_from_unsupported_url():
    result = image_downloader._get_extension_from_url(
        "https://example.com/photo.txt"
    )

    assert result is None


def test_download_image_uses_content_type(
    tmp_path,
    monkeypatch,
):
    download_dir = tmp_path / "downloads"

    monkeypatch.setattr(
        image_downloader,
        "ensure_download_directory",
        lambda: download_dir.mkdir(
            parents=True,
            exist_ok=True,
        ),
    )

    monkeypatch.setattr(
        image_downloader,
        "get_next_filename",
        lambda prefix, extension:
            download_dir / f"{prefix}1.{extension}",
    )

    response = FakeResponse(
        b"fake jpeg data",
        "image/jpeg",
    )

    def fake_urlopen(request, timeout):
        return response

    monkeypatch.setattr(
        image_downloader,
        "urlopen",
        fake_urlopen,
    )

    result = image_downloader.download_image(
        "https://example.com/image"
    )

    assert result == download_dir / "image1.jpg"
    assert result.exists()
    assert result.read_bytes() == b"fake jpeg data"


def test_download_image_falls_back_to_url_extension(
    tmp_path,
    monkeypatch,
):
    download_dir = tmp_path / "downloads"

    monkeypatch.setattr(
        image_downloader,
        "ensure_download_directory",
        lambda: download_dir.mkdir(
            parents=True,
            exist_ok=True,
        ),
    )

    monkeypatch.setattr(
        image_downloader,
        "get_next_filename",
        lambda prefix, extension:
            download_dir / f"{prefix}1.{extension}",
    )

    response = FakeResponse(
        b"fake png data",
        "application/octet-stream",
    )

    def fake_urlopen(request, timeout):
        return response

    monkeypatch.setattr(
        image_downloader,
        "urlopen",
        fake_urlopen,
    )

    result = image_downloader.download_image(
        "https://example.com/image.png"
    )

    assert result == download_dir / "image1.png"
    assert result.exists()
    assert result.read_bytes() == b"fake png data"


def test_content_type_takes_priority_over_url_extension(
    tmp_path,
    monkeypatch,
):
    download_dir = tmp_path / "downloads"

    monkeypatch.setattr(
        image_downloader,
        "ensure_download_directory",
        lambda: download_dir.mkdir(
            parents=True,
            exist_ok=True,
        ),
    )

    monkeypatch.setattr(
        image_downloader,
        "get_next_filename",
        lambda prefix, extension:
            download_dir / f"{prefix}1.{extension}",
    )

    response = FakeResponse(
        b"fake webp data",
        "image/webp",
    )

    def fake_urlopen(request, timeout):
        return response

    monkeypatch.setattr(
        image_downloader,
        "urlopen",
        fake_urlopen,
    )

    result = image_downloader.download_image(
        "https://example.com/image.jpg"
    )

    assert result == download_dir / "image1.webp"
    assert result.read_bytes() == b"fake webp data"


def test_download_image_rejects_unsupported_image(
    tmp_path,
    monkeypatch,
):
    download_dir = tmp_path / "downloads"

    monkeypatch.setattr(
        image_downloader,
        "ensure_download_directory",
        lambda: download_dir.mkdir(
            parents=True,
            exist_ok=True,
        ),
    )

    response = FakeResponse(
        b"not an image",
        "application/octet-stream",
    )

    def fake_urlopen(request, timeout):
        return response

    monkeypatch.setattr(
        image_downloader,
        "urlopen",
        fake_urlopen,
    )

    with pytest.raises(
        RuntimeError,
        match="supported image",
    ):
        image_downloader.download_image(
            "https://example.com/file"
        )


def test_download_image_wraps_network_error(
    tmp_path,
    monkeypatch,
):
    download_dir = tmp_path / "downloads"

    monkeypatch.setattr(
        image_downloader,
        "ensure_download_directory",
        lambda: download_dir.mkdir(
            parents=True,
            exist_ok=True,
        ),
    )

    def fake_urlopen(request, timeout):
        raise OSError("Connection failed")

    monkeypatch.setattr(
        image_downloader,
        "urlopen",
        fake_urlopen,
    )

    with pytest.raises(
        RuntimeError,
        match="Image download failed: Connection failed",
    ):
        image_downloader.download_image(
            "https://example.com/image.jpg"
        )


def test_download_image_sends_user_agent(
    tmp_path,
    monkeypatch,
):
    download_dir = tmp_path / "downloads"

    monkeypatch.setattr(
        image_downloader,
        "ensure_download_directory",
        lambda: download_dir.mkdir(
            parents=True,
            exist_ok=True,
        ),
    )

    monkeypatch.setattr(
        image_downloader,
        "get_next_filename",
        lambda prefix, extension:
            download_dir / f"{prefix}1.{extension}",
    )

    response = FakeResponse(
        b"image data",
        "image/png",
    )

    captured_request = SimpleNamespace()

    def fake_urlopen(request, timeout):
        captured_request.request = request
        captured_request.timeout = timeout
        return response

    monkeypatch.setattr(
        image_downloader,
        "urlopen",
        fake_urlopen,
    )

    result = image_downloader.download_image(
        "https://example.com/image"
    )

    assert result.exists()
    assert captured_request.timeout == 30

    user_agent = next(
        (
            value
            for key, value
            in captured_request.request.headers.items()
            if key.lower() == "user-agent"
        ),
        None,
    )

    assert user_agent is not None
    assert user_agent.startswith("Mozilla/5.0")