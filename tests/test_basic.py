"""Test with basic.yml."""

import helper
import pytest
from ruamel.yaml import os

import dotbackup


@pytest.fixture(autouse=True)
def _clean_test(monkeypatch):
    helper.clean_test(monkeypatch)


class TestBasic:
    _config = helper.get_config("basic")
    _files = list(helper.file_iterator(_config))
    # name a file belongs to app_a instead of a directory,
    # this can simplify mock file creation logic
    _files[0] += "/a.txt"
    _backup_files = list(
        map(lambda file, func=_config._get_backup_file_path: str(func(file)), _files)
    )

    @pytest.fixture(autouse=True)
    def _prepare(self):
        helper.cp(helper.get_config_path("basic"), helper.CONFIG_FILE)

    def _generate_hooks_out(self, command: str, apps: list) -> str:
        """Generate hooks stdout."""

        out = f"pre_{command} {self._config._backup_dir}\n"
        if apps == [] or "app_a" in apps:
            out += (
                f"app_a pre_{command} {self._config._backup_dir}\n"
                f"app_a post_{command} {self._config._backup_dir}\n"
            )
        if apps == [] or "app_b" in apps:
            out += (
                f"app_b pre_{command} {self._config._backup_dir}\n"
                f"app_b post_{command} {self._config._backup_dir}\n"
            )
        out += f"post_{command} {self._config._backup_dir}\n"

        return out

    def test_backup_file_not_found(self, caplog):
        """Test file not found situation when backing up."""

        assert dotbackup.dotbackup() == 0
        for file in helper.file_iterator(self._config):
            assert f"file not found: {file}: skip backing up this file" in caplog.text

    def test_setup_file_not_found(self, caplog):
        """Test file not found situation when setting up."""

        assert dotbackup.dotsetup() == 0
        for file in helper.file_iterator(self._config):
            src_path = self._config._get_backup_file_path(file)
            assert (
                f"file not found: {src_path}: skip setting up this file" in caplog.text
            )

    @pytest.mark.parametrize("apps", [[], ["app_a"], ["app_b"], ["app_a", "app_b"]])
    def test_backup(self, apps, capfd):
        """Test basic backup, check files and hooks."""

        hooks_out = self._generate_hooks_out("backup", apps)

        for file in self._files:
            if apps and not any(map(lambda app: app in file, apps)):
                continue

            helper.create_file(file, helper.random_str())

        assert dotbackup.dotbackup(apps) == 0
        assert helper.validate_backup(self._config)
        assert capfd.readouterr().out == hooks_out

        helper.rmdir("~/backup")
        assert dotbackup.main(["backup"] + apps) == 0
        assert helper.validate_backup(self._config)
        assert capfd.readouterr().out == hooks_out

    @pytest.mark.parametrize("apps", [[], ["app_a"], ["app_b"], ["app_a", "app_b"]])
    def test_setup(self, apps, capfd):
        """Test basic setup, check files and hooks."""

        hooks_out = self._generate_hooks_out("setup", apps)

        for file in self._backup_files:
            if apps and not any(map(lambda app: app in file, apps)):
                continue

            helper.create_file(file, helper.random_str())

        assert dotbackup.dotsetup(apps) == 0
        assert helper.validate_setup(self._config)
        assert capfd.readouterr().out == hooks_out

        helper.rmdir("~/.config/app_a")
        helper.rmdir("~/.config/app_b")
        assert dotbackup.main(["setup"] + apps) == 0
        assert helper.validate_setup(self._config)
        assert capfd.readouterr().out == hooks_out

    def test_clean_backup(self):
        """Test backup with --clean option."""

        # create dirty backup files
        for file in self._backup_files:
            helper.create_file(file, helper.random_str())

        helper.mkdir("~/.config/app_a")

        assert dotbackup.dotbackup(["--clean"]) == 0
        assert helper.validate_backup(self._config)
        for file in self._backup_files:
            assert not os.path.isfile(file)

    def test_clean_setup(self):
        """Test setup with --clean option."""

        # create dirty configuration files
        for file in self._files:
            helper.create_file(file, helper.random_str())

        helper.mkdir("~/backup/.config/app_a")

        assert dotbackup.dotsetup(["--clean"]) == 0
        assert helper.validate_setup(self._config)
        for file in self._files:
            assert not os.path.isfile(file)

    @pytest.mark.parametrize("option", ["-l", "--list"])
    def test_list(self, option, capfd):
        """Test -l, --list option."""
        expected_output = "\n".join(self._config._apps_dict.keys()) + "\n"

        with pytest.raises(SystemExit):
            dotbackup.dotbackup([option])
        assert capfd.readouterr().out == expected_output
        with pytest.raises(SystemExit):
            dotbackup.dotsetup([option])
        assert capfd.readouterr().out == expected_output

        with pytest.raises(SystemExit):
            dotbackup.main(["backup", option])
        assert capfd.readouterr().out == expected_output
        with pytest.raises(SystemExit):
            dotbackup.main(["setup", option])
        assert capfd.readouterr().out == expected_output
