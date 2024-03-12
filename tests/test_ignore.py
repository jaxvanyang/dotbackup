"""Test with ignore.yml."""

import os
from itertools import chain

import helper
import pytest

import dotbackup


class TestIgnore:
    @pytest.fixture(autouse=True)
    def _prepare(self, monkeypatch):
        helper.clean_test(monkeypatch)
        helper.cp(helper.get_config_path("ignore"), helper.CONFIG_FILE)

    _config = helper.get_config("ignore")
    _files = ["~/.config/app/global_ignore", "~/.config/app/app_ignore"]
    _ignore_files = [
        "~/.config/app/ignore/global_ignore",
        "~/.config/app/ignore/app_ignore",
    ]
    _backup_files = list(
        map(lambda file, func=_config._get_backup_file_path: str(func(file)), _files)
    )
    _backup_ignore_files = list(
        map(
            lambda file, func=_config._get_backup_file_path: str(func(file)),
            _ignore_files,
        )
    )

    def test_backup(self):
        for file in chain(self._files, self._ignore_files):
            helper.create_file(file, helper.random_str())

        assert dotbackup.dotbackup() == 0
        assert not helper.validate_backup(self._config)
        assert helper.validate_backup(self._config, False)
        for file in self._backup_ignore_files:
            assert not os.path.isfile(file)

    def test_setup(self):
        for file in chain(self._backup_files, self._backup_ignore_files):
            helper.create_file(file, helper.random_str())

        assert dotbackup.dotsetup() == 0
        assert not helper.validate_setup(self._config)
        assert helper.validate_setup(self._config, False)
        for file in self._ignore_files:
            assert not os.path.isfile(self._config._normpath(file))
