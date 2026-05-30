"""Config loading and validation."""

import os

import pytest

from gradescope_autosubmitter.config import EXAMPLE_CONFIG, Config


def test_load_config(config_file):
    cfg = Config(str(config_file))
    assert cfg.get("course") == "cab201"
    assert cfg.get("assignment") == "t6q1"
    assert cfg.get("zip_name") == "out.zip"
    assert cfg.include_patterns() == ["*.py"]


def test_validate_requires_course_and_assignment(tmp_path):
    path = tmp_path / "gradescope.yml"
    path.write_text("course: x\n", encoding="utf-8")
    with pytest.raises(ValueError, match="assignment"):
        Config(str(path)).validate()


def test_bundle_alias_for_include(tmp_path):
    path = tmp_path / "gradescope.yml"
    path.write_text(
        'course: "a"\nassignment: "b"\nbundle:\n  - "*.txt"\n',
        encoding="utf-8",
    )
    assert Config(str(path)).include_patterns() == ["*.txt"]


def test_env_override_include(monkeypatch):
    monkeypatch.setenv("GRADESCOPE_INCLUDE", "*.java,*.kt")
    cfg = Config()
    assert cfg.include_patterns() == ["*.java", "*.kt"]


def test_env_override_headless(monkeypatch, config_file):
    monkeypatch.setenv("GRADESCOPE_HEADLESS", "true")
    cfg = Config(str(config_file))
    assert cfg.get("headless") is True


def test_legacy_file_key_maps_to_zip_name(tmp_path):
    path = tmp_path / "gradescope.yml"
    path.write_text(
        'course: "a"\nassignment: "b"\nfile: legacy.zip\n',
        encoding="utf-8",
    )
    assert Config(str(path)).get("zip_name") == "legacy.zip"


def test_init_template_has_quoted_course(config_file):
    assert 'course: "cab201"' in EXAMPLE_CONFIG
    assert "include:" in EXAMPLE_CONFIG
    assert "credentials" not in EXAMPLE_CONFIG


def test_create_example_config(tmp_path):
    out = tmp_path / "new.yml"
    Config().create_example_config(str(out))
    loaded = Config(str(out))
    loaded.validate()
