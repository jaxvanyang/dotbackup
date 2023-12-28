import helper
import pytest

import dotbackup


@pytest.fixture(autouse=True)
def _prepare_test(monkeypatch):
    helper.prepare_test(monkeypatch)


def test_parse_args():
    args = dotbackup.parse_args([])
    assert (args.config, args.command, args.app) == (helper.CONFIG_FILE, "backup", [])


@pytest.mark.parametrize("config_path", helper.CONFIG_PATHS)
def test_parse_config(config_path):
    config = dotbackup.parse_config(helper.get_config_path(config_path))
    mock_config = helper.get_config(config_path)
    assert config == mock_config
    assert str(config) == str(mock_config)


class TestBackup:
    def _check_hook_out(self, capfd, apps=None):
        dotbackup.backup(helper.ONLY_HOOKS_CONFIG, apps)
        assert capfd.readouterr().out == helper.generate_hook_out(apps=apps)

    def test_unknown_app(self, capfd):
        with pytest.raises(SystemExit):
            dotbackup.backup(helper.ONLY_HOOKS_CONFIG, ["unknown"])
        assert "application not configured: unknown" in capfd.readouterr().err

    def test_backup_dir_not_found(self, capfd):
        with pytest.raises(SystemExit):
            dotbackup.backup(helper.ONLY_HOOKS_CONFIG)
        assert "backup directory not found" in capfd.readouterr().err

    @pytest.mark.parametrize("apps", helper.APPS_CHOICE)
    def test_default(self, capfd, apps):
        helper.mkdir(helper.BACKUP_DIR)
        self._check_hook_out(capfd, apps)


class TestSetup:
    def _check_hook_out(self, capfd, apps=None):
        dotbackup.setup(helper.ONLY_HOOKS_CONFIG, apps)
        assert capfd.readouterr().out == helper.generate_hook_out("setup", apps)

    def test_unknown_app(self, capfd):
        with pytest.raises(SystemExit):
            dotbackup.setup(helper.ONLY_HOOKS_CONFIG, ["unknown"])
        assert "application not configured: unknown" in capfd.readouterr().err

    def test_backup_dir_not_found(self, capfd):
        with pytest.raises(SystemExit):
            dotbackup.setup(helper.ONLY_HOOKS_CONFIG)
        assert "backup directory not found" in capfd.readouterr().err

    @pytest.mark.parametrize("apps", helper.APPS_CHOICE)
    def test_default(self, capfd, apps):
        helper.mkdir(helper.BACKUP_DIR)
        self._check_hook_out(capfd, apps)


@pytest.mark.parametrize("apps", helper.APPS_CHOICE)
class TestMain:
    @pytest.fixture(autouse=True)
    def _prepare(self):
        helper.mkdir(helper.BACKUP_DIR)
        helper.cp(helper.get_config_path("only_hooks.yml"), helper.CONFIG_FILE)

    def test_default(self, capfd, apps):
        dotbackup.main(apps)
        assert capfd.readouterr().out == helper.generate_hook_out(apps=apps)

    def test_backup(self, capfd, apps):
        dotbackup.main(["backup"] + apps)
        assert capfd.readouterr().out == helper.generate_hook_out(apps=apps)

    def test_setup(self, capfd, apps):
        dotbackup.main(["setup"] + apps)
        assert capfd.readouterr().out == helper.generate_hook_out("setup", apps)
