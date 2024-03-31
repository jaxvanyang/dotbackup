"""Miscellaneous tests."""

import os

import helper
import pytest

import dotbackup
from dotbackup import Config


@pytest.fixture(autouse=True)
def _clean_test(monkeypatch):
    helper.clean_test(monkeypatch)


def test_empty():
    helper.create_file(helper.CONFIG_FILE)

    assert dotbackup.dotbackup() == 1
    assert dotbackup.dotsetup() == 1
    assert dotbackup.main(["backup"]) == 1
    assert dotbackup.main(["setup"]) == 1


@pytest.mark.parametrize("option", ["-V", "--version"])
def test_version(option, capfd):
    assert dotbackup.dotbackup([option]) == 0
    assert capfd.readouterr().out == f"dotbackup {dotbackup.__VERSION__}\n"
    assert dotbackup.dotsetup([option]) == 0
    assert capfd.readouterr().out == f"dotbackup {dotbackup.__VERSION__}\n"

    assert dotbackup.main([option]) == 0
    assert capfd.readouterr().out == f"dotbackup {dotbackup.__VERSION__}\n"
    assert dotbackup.main(["backup", option]) == 0
    assert capfd.readouterr().out == f"dotbackup {dotbackup.__VERSION__}\n"
    assert dotbackup.main(["setup", option]) == 0
    assert capfd.readouterr().out == f"dotbackup {dotbackup.__VERSION__}\n"


def test_shortcut(monkeypatch):
    """Test configuration shortcut."""

    parser = Config.dotsetup_parser()
    args = parser.parse_args(["-c", "basic"])
    basic_config = helper.get_config("basic")
    basic_config._dict["selected_apps"] = []
    config_path = f"{helper.CONFIG_DIR}/basic.yml"

    helper.cp(helper.get_config_path("basic"), config_path)
    config = Config.parse_args(args)
    assert config == basic_config

    os.rename(config_path, f"{helper.TEST_HOME}/basic")
    monkeypatch.chdir(helper.TEST_HOME)
    monkeypatch.setenv("PWD", f"{os.environ['PWD']}/{helper.TEST_HOME}")
    config = Config.parse_args(args)
    assert config == basic_config
