"""Test with complex_script.yml."""

import helper
import pytest

import dotbackup


@pytest.fixture(autouse=True)
def _clean_test(monkeypatch):
    helper.clean_test(monkeypatch)


def test_complex_script(capfd):
    helper.cp(helper.get_config_path("complex_script"), helper.CONFIG_FILE)

    dotbackup.dotbackup()
    assert capfd.readouterr().out == "hello world\nhello world\n"

    dotbackup.dotsetup()
    assert capfd.readouterr().out == ""
