from pathlib import Path

import pytest

import src.processors as processors


def test_check_ffmpeg_when_available(monkeypatch):
    monkeypatch.setattr(
        processors.shutil,
        "which",
        lambda name: r"C:\ffmpeg\bin\ffmpeg.exe",
    )

    available, info = processors.check_ffmpeg()

    assert available is True
    assert info == r"C:\ffmpeg\bin\ffmpeg.exe"


def test_check_ffmpeg_when_missing(monkeypatch):
    monkeypatch.setattr(
        processors.shutil,
        "which",
        lambda name: None,
    )

    available, info = processors.check_ffmpeg()

    assert available is False
    assert info == "FFmpeg was not found on PATH."


def test_check_ffprobe_when_available(monkeypatch):
    monkeypatch.setattr(
        processors.shutil,
        "which",
        lambda name: r"C:\ffmpeg\bin\ffprobe.exe",
    )

    available, info = processors.check_ffprobe()

    assert available is True
    assert info == r"C:\ffmpeg\bin\ffprobe.exe"


def test_check_ffprobe_when_missing(monkeypatch):
    monkeypatch.setattr(
        processors.shutil,
        "which",
        lambda name: None,
    )

    available, info = processors.check_ffprobe()

    assert available is False
    assert info == "FFprobe was not found on PATH."


def test_get_media_streams_video_and_audio(monkeypatch):
    monkeypatch.setattr(
        processors,
        "check_ffprobe",
        lambda: (True, "ffprobe.exe"),
    )

    responses = [
        type("Result", (), {"stdout": "video\n"})(),
        type("Result", (), {"stdout": "audio\n"})(),
    ]

    def fake_run(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(processors.subprocess, "run", fake_run)

    result = processors.get_media_streams(
        Path("sample.mp4")
    )

    assert result == (True, True)


def test_get_media_streams_video_only(monkeypatch):
    monkeypatch.setattr(
        processors,
        "check_ffprobe",
        lambda: (True, "ffprobe.exe"),
    )

    responses = [
        type("Result", (), {"stdout": "video\n"})(),
        type("Result", (), {"stdout": ""})(),
    ]

    def fake_run(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(processors.subprocess, "run", fake_run)

    result = processors.get_media_streams(
        Path("sample.mp4")
    )

    assert result == (True, False)


def test_get_media_streams_audio_only(monkeypatch):
    monkeypatch.setattr(
        processors,
        "check_ffprobe",
        lambda: (True, "ffprobe.exe"),
    )

    responses = [
        type("Result", (), {"stdout": ""})(),
        type("Result", (), {"stdout": "audio\n"})(),
    ]

    def fake_run(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(processors.subprocess, "run", fake_run)

    result = processors.get_media_streams(
        Path("sample.mp3")
    )

    assert result == (False, True)


def test_get_media_streams_no_video_or_audio(monkeypatch):
    monkeypatch.setattr(
        processors,
        "check_ffprobe",
        lambda: (True, "ffprobe.exe"),
    )

    responses = [
        type("Result", (), {"stdout": ""})(),
        type("Result", (), {"stdout": ""})(),
    ]

    def fake_run(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(processors.subprocess, "run", fake_run)

    result = processors.get_media_streams(
        Path("unknown.media")
    )

    assert result == (False, False)


def test_get_media_streams_when_ffprobe_missing(monkeypatch):
    monkeypatch.setattr(
        processors,
        "check_ffprobe",
        lambda: (
            False,
            "FFprobe was not found on PATH.",
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="FFprobe was not found on PATH.",
    ):
        processors.get_media_streams(
            Path("sample.mp4")
        )