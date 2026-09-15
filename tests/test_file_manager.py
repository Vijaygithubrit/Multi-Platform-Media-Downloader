from pathlib import Path

import src.file_manager as file_manager


def test_ensure_download_directory(tmp_path, monkeypatch):
    download_dir = tmp_path / "downloads"

    monkeypatch.setattr(file_manager, "DOWNLOAD_DIR", download_dir)

    assert not download_dir.exists()

    file_manager.ensure_download_directory()

    assert download_dir.exists()
    assert download_dir.is_dir()


def test_first_number_is_one(tmp_path, monkeypatch):
    download_dir = tmp_path / "downloads"

    monkeypatch.setattr(file_manager, "DOWNLOAD_DIR", download_dir)

    assert file_manager.get_next_number("video", "mp4") == 1


def test_next_number_after_existing_files(tmp_path, monkeypatch):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()

    (download_dir / "video1.mp4").touch()
    (download_dir / "video2.mp4").touch()
    (download_dir / "video3.mp4").touch()

    monkeypatch.setattr(file_manager, "DOWNLOAD_DIR", download_dir)

    assert file_manager.get_next_number("video", "mp4") == 4


def test_deleted_number_is_not_reused(tmp_path, monkeypatch):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()

    (download_dir / "video1.mp4").touch()
    (download_dir / "video3.mp4").touch()

    monkeypatch.setattr(file_manager, "DOWNLOAD_DIR", download_dir)

    assert file_manager.get_next_number("video", "mp4") == 4


def test_different_extension_is_ignored(tmp_path, monkeypatch):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()

    (download_dir / "video1.mp4").touch()
    (download_dir / "video9.mkv").touch()

    monkeypatch.setattr(file_manager, "DOWNLOAD_DIR", download_dir)

    assert file_manager.get_next_number("video", "mp4") == 2


def test_different_prefix_is_ignored(tmp_path, monkeypatch):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()

    (download_dir / "audio5.mp3").touch()
    (download_dir / "video2.mp4").touch()

    monkeypatch.setattr(file_manager, "DOWNLOAD_DIR", download_dir)

    assert file_manager.get_next_number("video", "mp4") == 3


def test_case_insensitive_matching(tmp_path, monkeypatch):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()

    (download_dir / "VIDEO3.MP4").touch()

    monkeypatch.setattr(file_manager, "DOWNLOAD_DIR", download_dir)

    assert file_manager.get_next_number("video", "mp4") == 4


def test_non_numbered_file_is_ignored(tmp_path, monkeypatch):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()

    (download_dir / "video.mp4").touch()
    (download_dir / "video_test.mp4").touch()
    (download_dir / "videoABC.mp4").touch()

    monkeypatch.setattr(file_manager, "DOWNLOAD_DIR", download_dir)

    assert file_manager.get_next_number("video", "mp4") == 1


def test_directories_are_ignored(tmp_path, monkeypatch):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()

    (download_dir / "video1.mp4").mkdir()

    monkeypatch.setattr(file_manager, "DOWNLOAD_DIR", download_dir)

    assert file_manager.get_next_number("video", "mp4") == 1


def test_get_next_filename(tmp_path, monkeypatch):
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()

    (download_dir / "video1.mp4").touch()
    (download_dir / "video2.mp4").touch()

    monkeypatch.setattr(file_manager, "DOWNLOAD_DIR", download_dir)

    result = file_manager.get_next_filename("video", "mp4")

    assert result == download_dir / "video3.mp4"
    assert isinstance(result, Path)


def test_extension_with_dot(tmp_path, monkeypatch):
    download_dir = tmp_path / "downloads"

    monkeypatch.setattr(file_manager, "DOWNLOAD_DIR", download_dir)

    result = file_manager.get_next_filename("audio", ".mp3")

    assert result == download_dir / "audio1.mp3"