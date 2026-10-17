from smart_flow.config import Settings


def test_default_log_level(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    assert Settings.from_env().log_level == "INFO"


def test_log_level_is_uppercased(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "debug")
    assert Settings.from_env().log_level == "DEBUG"


def test_ensure_dirs_creates_folders(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    settings = Settings.from_env()
    settings.ensure_dirs()

    assert settings.inbox_dir.is_dir()
    assert settings.processed_dir.is_dir()
    assert settings.failed_dir.is_dir()
