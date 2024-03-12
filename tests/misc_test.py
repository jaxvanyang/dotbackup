"""Miscellaneous tests."""

import helper
import pytest

import dotbackup


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
