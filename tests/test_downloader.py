from pathlib import Path
import shutil

import pytest
import yt_dlp

import src.downloader as downloader


class FakeTemporaryDirectory:
    def __init__(self, directory):
        self.directory = Path(directory)

    def __enter__(self):
        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )
        return str(self.directory)

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(
            self.directory,
            ignore_errors=True,
        )
        return False


class FakeYoutubeDL:
    def __init__(
        self,
        options,
        output_extension=None,
        error=None,
    ):
        self.options = options
        self.output_extension = output_extension
        self.error = error

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def download(self, urls):
        if self.error:
            raise self.error

        if self.output_extension is None:
            return

        output_template = self.options["outtmpl"]

        output_path = Path(
            output_template.replace(
                "%(ext)s",
                self.output_extension,
            )
        )

        output_path.write_bytes(
            b"fake media data"
        )


def setup_video_environment(
    tmp_path,
    monkeypatch,
    output_extension="mp4",
    streams=(True, True),
):
    final_path = tmp_path / "downloads" / "video1.mp4"
    temp_directory = tmp_path / "video_temp"

    final_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    monkeypatch.setattr(
        downloader,
        "ensure_download_directory",
        lambda: None,
    )

    monkeypatch.setattr(
        downloader,
        "check_ffmpeg",
        lambda: (True, "ffmpeg"),
    )

    monkeypatch.setattr(
        downloader,
        "get_next_filename",
        lambda prefix, extension: final_path,
    )

    monkeypatch.setattr(
        downloader.tempfile,
        "TemporaryDirectory",
        lambda prefix: FakeTemporaryDirectory(
            temp_directory
        ),
    )

    monkeypatch.setattr(
        downloader,
        "get_media_streams",
        lambda file_path: streams,
    )

    fake_ytdlp = FakeYoutubeDL(
        options={},
        output_extension=output_extension,
    )

    monkeypatch.setattr(
        downloader.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options=options,
            output_extension=output_extension,
        ),
    )

    return final_path, temp_directory


def setup_audio_environment(
    tmp_path,
    monkeypatch,
    output_extension="mp3",
):
    final_path = tmp_path / "downloads" / "audio1.mp3"
    temp_directory = tmp_path / "audio_temp"

    final_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    monkeypatch.setattr(
        downloader,
        "ensure_download_directory",
        lambda: None,
    )

    monkeypatch.setattr(
        downloader,
        "check_ffmpeg",
        lambda: (True, "ffmpeg"),
    )

    monkeypatch.setattr(
        downloader,
        "get_next_filename",
        lambda prefix, extension: final_path,
    )

    monkeypatch.setattr(
        downloader.tempfile,
        "TemporaryDirectory",
        lambda prefix: FakeTemporaryDirectory(
            temp_directory
        ),
    )

    monkeypatch.setattr(
        downloader.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options=options,
            output_extension=output_extension,
        ),
    )

    return final_path, temp_directory


# ============================================================
# _find_downloaded_file TESTS
# ============================================================


def test_find_downloaded_file_returns_none_for_empty_directory(
    tmp_path,
):
    result = downloader._find_downloaded_file(
        tmp_path
    )

    assert result is None


def test_find_downloaded_file_prefers_media_extension(
    tmp_path,
):
    text_file = tmp_path / "random.txt"
    video_file = tmp_path / "source.mp4"

    text_file.write_text("text")
    video_file.write_bytes(b"video")

    result = downloader._find_downloaded_file(
        tmp_path
    )

    assert result == video_file


def test_find_downloaded_file_returns_first_file_if_no_preferred_extension(
    tmp_path,
):
    file_path = tmp_path / "source.xyz"

    file_path.write_bytes(b"data")

    result = downloader._find_downloaded_file(
        tmp_path
    )

    assert result == file_path


# ============================================================
# VIDEO DOWNLOADER TESTS
# ============================================================


def test_download_video_success(
    tmp_path,
    monkeypatch,
):
    final_path, temp_directory = setup_video_environment(
        tmp_path,
        monkeypatch,
    )

    result = downloader.download_video(
        "https://example.com/video"
    )

    assert result == final_path
    assert result.exists()
    assert result.read_bytes() == b"fake media data"

    # Temporary directory must be cleaned up.
    assert not temp_directory.exists()


def test_download_video_uses_correct_yt_dlp_options(
    tmp_path,
    monkeypatch,
):
    final_path = tmp_path / "downloads" / "video1.mp4"
    temp_directory = tmp_path / "video_temp"

    captured_options = {}

    final_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    monkeypatch.setattr(
        downloader,
        "ensure_download_directory",
        lambda: None,
    )

    monkeypatch.setattr(
        downloader,
        "check_ffmpeg",
        lambda: (True, "ffmpeg"),
    )

    monkeypatch.setattr(
        downloader,
        "get_next_filename",
        lambda prefix, extension: final_path,
    )

    monkeypatch.setattr(
        downloader.tempfile,
        "TemporaryDirectory",
        lambda prefix: FakeTemporaryDirectory(
            temp_directory
        ),
    )

    monkeypatch.setattr(
        downloader,
        "get_media_streams",
        lambda file_path: (True, True),
    )

    def fake_youtube_dl(options):
        captured_options.update(options)

        return FakeYoutubeDL(
            options=options,
            output_extension="mp4",
        )

    monkeypatch.setattr(
        downloader.yt_dlp,
        "YoutubeDL",
        fake_youtube_dl,
    )

    downloader.download_video(
        "https://example.com/video"
    )

    assert (
        captured_options["format"]
        == (
            "bestvideo[vcodec^=avc1]+"
            "bestaudio[acodec^=mp4a]/"
            "best[ext=mp4]/"
            "best"
        )
    )

    assert captured_options["merge_output_format"] == "mp4"
    assert captured_options["noplaylist"] is True
    assert captured_options["ffmpeg_location"] == "ffmpeg"
    assert captured_options["writesubtitles"] is False
    assert captured_options["writeautomaticsub"] is False
    assert captured_options["writethumbnail"] is False
    assert captured_options["keepvideo"] is False


def test_download_video_fails_when_ffmpeg_missing(
    monkeypatch,
):
    monkeypatch.setattr(
        downloader,
        "check_ffmpeg",
        lambda: (
            False,
            "FFmpeg was not found on PATH.",
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="FFmpeg was not found on PATH",
    ):
        downloader.download_video(
            "https://example.com/video"
        )


def test_download_video_handles_ytdlp_error(
    tmp_path,
    monkeypatch,
):
    final_path = tmp_path / "downloads" / "video1.mp4"
    temp_directory = tmp_path / "video_temp"

    final_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    error = yt_dlp.utils.DownloadError(
        "Test video download failure"
    )

    monkeypatch.setattr(
        downloader,
        "ensure_download_directory",
        lambda: None,
    )

    monkeypatch.setattr(
        downloader,
        "check_ffmpeg",
        lambda: (True, "ffmpeg"),
    )

    monkeypatch.setattr(
        downloader,
        "get_next_filename",
        lambda prefix, extension: final_path,
    )

    monkeypatch.setattr(
        downloader.tempfile,
        "TemporaryDirectory",
        lambda prefix: FakeTemporaryDirectory(
            temp_directory
        ),
    )

    monkeypatch.setattr(
        downloader.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options=options,
            error=error,
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="Video download/merge failed",
    ):
        downloader.download_video(
            "https://example.com/video"
        )

    assert not final_path.exists()
    assert not temp_directory.exists()


def test_download_video_fails_when_no_file_is_created(
    tmp_path,
    monkeypatch,
):
    final_path, temp_directory = setup_video_environment(
        tmp_path,
        monkeypatch,
        output_extension=None,
    )

    with pytest.raises(
        RuntimeError,
        match="no video file was found",
    ):
        downloader.download_video(
            "https://example.com/video"
        )

    assert not final_path.exists()
    assert not temp_directory.exists()


def test_download_video_handles_stream_verification_error(
    tmp_path,
    monkeypatch,
):
    final_path, temp_directory = setup_video_environment(
        tmp_path,
        monkeypatch,
    )

    monkeypatch.setattr(
        downloader,
        "get_media_streams",
        lambda file_path: (
            (_ for _ in ()).throw(
                RuntimeError("FFprobe failure")
            )
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="Could not verify the downloaded video",
    ):
        downloader.download_video(
            "https://example.com/video"
        )

    assert not final_path.exists()
    assert not temp_directory.exists()


def test_download_video_fails_without_video_stream(
    tmp_path,
    monkeypatch,
):
    final_path, temp_directory = setup_video_environment(
        tmp_path,
        monkeypatch,
        streams=(False, True),
    )

    with pytest.raises(
        RuntimeError,
        match="does not contain a video stream",
    ):
        downloader.download_video(
            "https://example.com/video"
        )

    assert not final_path.exists()
    assert not temp_directory.exists()


def test_download_video_fails_without_audio_stream(
    tmp_path,
    monkeypatch,
):
    final_path, temp_directory = setup_video_environment(
        tmp_path,
        monkeypatch,
        streams=(True, False),
    )

    with pytest.raises(
        RuntimeError,
        match="does not contain an audio stream",
    ):
        downloader.download_video(
            "https://example.com/video"
        )

    assert not final_path.exists()
    assert not temp_directory.exists()


def test_download_video_handles_move_error(
    tmp_path,
    monkeypatch,
):
    final_path, temp_directory = setup_video_environment(
        tmp_path,
        monkeypatch,
    )

    def fake_move(source, destination):
        raise OSError("Move failed")

    monkeypatch.setattr(
        downloader.shutil,
        "move",
        fake_move,
    )

    with pytest.raises(
        RuntimeError,
        match="Could not save the final video",
    ):
        downloader.download_video(
            "https://example.com/video"
        )

    assert not final_path.exists()
    assert not temp_directory.exists()


# ============================================================
# AUDIO DOWNLOADER TESTS
# ============================================================


def test_download_audio_success(
    tmp_path,
    monkeypatch,
):
    final_path, temp_directory = setup_audio_environment(
        tmp_path,
        monkeypatch,
    )

    result = downloader.download_audio(
        "https://example.com/audio"
    )

    assert result == final_path
    assert result.exists()
    assert result.read_bytes() == b"fake media data"

    assert not temp_directory.exists()


def test_download_audio_uses_correct_yt_dlp_options(
    tmp_path,
    monkeypatch,
):
    final_path = tmp_path / "downloads" / "audio1.mp3"
    temp_directory = tmp_path / "audio_temp"

    captured_options = {}

    final_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    monkeypatch.setattr(
        downloader,
        "ensure_download_directory",
        lambda: None,
    )

    monkeypatch.setattr(
        downloader,
        "check_ffmpeg",
        lambda: (True, "ffmpeg"),
    )

    monkeypatch.setattr(
        downloader,
        "get_next_filename",
        lambda prefix, extension: final_path,
    )

    monkeypatch.setattr(
        downloader.tempfile,
        "TemporaryDirectory",
        lambda prefix: FakeTemporaryDirectory(
            temp_directory
        ),
    )

    def fake_youtube_dl(options):
        captured_options.update(options)

        return FakeYoutubeDL(
            options=options,
            output_extension="mp3",
        )

    monkeypatch.setattr(
        downloader.yt_dlp,
        "YoutubeDL",
        fake_youtube_dl,
    )

    downloader.download_audio(
        "https://example.com/audio"
    )

    assert captured_options["format"] == "bestaudio/best"
    assert captured_options["noplaylist"] is True
    assert captured_options["ffmpeg_location"] == "ffmpeg"
    assert captured_options["writesubtitles"] is False
    assert captured_options["writeautomaticsub"] is False
    assert captured_options["writethumbnail"] is False
    assert captured_options["keepvideo"] is False

    assert len(
        captured_options["postprocessors"]
    ) == 1

    postprocessor = (
        captured_options["postprocessors"][0]
    )

    assert (
        postprocessor["key"]
        == "FFmpegExtractAudio"
    )

    assert (
        postprocessor["preferredcodec"]
        == "mp3"
    )

    assert (
        postprocessor["preferredquality"]
        == "192"
    )


def test_download_audio_fails_when_ffmpeg_missing(
    monkeypatch,
):
    monkeypatch.setattr(
        downloader,
        "check_ffmpeg",
        lambda: (
            False,
            "FFmpeg was not found on PATH.",
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="FFmpeg was not found on PATH",
    ):
        downloader.download_audio(
            "https://example.com/audio"
        )


def test_download_audio_handles_ytdlp_error(
    tmp_path,
    monkeypatch,
):
    final_path = tmp_path / "downloads" / "audio1.mp3"
    temp_directory = tmp_path / "audio_temp"

    final_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    error = yt_dlp.utils.DownloadError(
        "Test audio download failure"
    )

    monkeypatch.setattr(
        downloader,
        "ensure_download_directory",
        lambda: None,
    )

    monkeypatch.setattr(
        downloader,
        "check_ffmpeg",
        lambda: (True, "ffmpeg"),
    )

    monkeypatch.setattr(
        downloader,
        "get_next_filename",
        lambda prefix, extension: final_path,
    )

    monkeypatch.setattr(
        downloader.tempfile,
        "TemporaryDirectory",
        lambda prefix: FakeTemporaryDirectory(
            temp_directory
        ),
    )

    monkeypatch.setattr(
        downloader.yt_dlp,
        "YoutubeDL",
        lambda options: FakeYoutubeDL(
            options=options,
            error=error,
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="Audio download failed",
    ):
        downloader.download_audio(
            "https://example.com/audio"
        )

    assert not final_path.exists()
    assert not temp_directory.exists()


def test_download_audio_fails_when_no_file_is_created(
    tmp_path,
    monkeypatch,
):
    final_path, temp_directory = setup_audio_environment(
        tmp_path,
        monkeypatch,
        output_extension=None,
    )

    with pytest.raises(
        RuntimeError,
        match="no audio file was found",
    ):
        downloader.download_audio(
            "https://example.com/audio"
        )

    assert not final_path.exists()
    assert not temp_directory.exists()


def test_download_audio_handles_move_error(
    tmp_path,
    monkeypatch,
):
    final_path, temp_directory = setup_audio_environment(
        tmp_path,
        monkeypatch,
    )

    def fake_move(source, destination):
        raise OSError("Move failed")

    monkeypatch.setattr(
        downloader.shutil,
        "move",
        fake_move,
    )

    with pytest.raises(
        RuntimeError,
        match="Could not save the final audio",
    ):
        downloader.download_audio(
            "https://example.com/audio"
        )

    assert not final_path.exists()
    assert not temp_directory.exists()