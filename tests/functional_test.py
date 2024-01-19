import helper
import pytest

import dotbackup


@pytest.fixture(autouse=True)
def _prepare_test(monkeypatch):
    helper.prepare_test(monkeypatch)


def test_empty(caplog):
    helper.create_file(helper.CONFIG_FILE)
    dotbackup.main()
    assert "empty configuration" in caplog.text


def test_complex_script(capfd):
    helper.cp(helper.get_config_path("complex_script.yml"), helper.CONFIG_FILE)

    dotbackup.main()
    assert capfd.readouterr().out == "hello world\nhello world\n"


def test_version(capfd):
    dotbackup.main(["-V"])
    assert capfd.readouterr().out == f"dotbackup {dotbackup.__VERSION__}\n"

    dotbackup.main(["--version"])
    assert capfd.readouterr().out == f"dotbackup {dotbackup.__VERSION__}\n"


class TestBasic:
    a_config_dir = f"{helper.CONFIG_DIR}/app_a"
    a_backup_dir = f"{helper.BACKUP_DIR}/app_a/.config/app_a"
    a_txt = f"{a_config_dir}/a.txt"
    a_legacy_txt = f"{a_config_dir}/a_legacy.txt"
    a_txt_backup = f"{a_backup_dir}/a.txt"
    a_legacy_txt_backup = f"{a_backup_dir}/a_legacy.txt"

    b_config_dir = f"{helper.CONFIG_DIR}/app_b"
    b_backup_dir = f"{helper.BACKUP_DIR}/app_b/.config/app_b"
    b1_txt = f"{b_config_dir}/b1.txt"
    b2_txt = f"{b_config_dir}/b2.txt"
    b1_txt_backup = f"{b_backup_dir}/b1.txt"
    b2_txt_backup = f"{b_backup_dir}/b2.txt"

    @pytest.fixture(autouse=True)
    def _prepare(self):
        helper.cp(helper.get_config_path("basic.yml"), helper.CONFIG_FILE)
        helper.mkdir(helper.BACKUP_DIR)

    def test_skip_backup(self, caplog):
        dotbackup.main()
        assert caplog.text.count("this file backup skipped") == 3

    def test_skip_setup(self, caplog):
        dotbackup.main(["setup"])
        assert caplog.text.count("this file setup skipped") == 3

    def test_backup(self, capfd):
        helper.create_file(self.a_txt, helper.random_str())
        helper.create_file(self.b1_txt, helper.random_str())
        helper.create_file(self.b2_txt, helper.random_str())

        dotbackup.main()
        assert helper.dirdiff(self.a_config_dir, self.a_backup_dir)
        assert helper.dirdiff(self.b_config_dir, self.b_backup_dir)
        assert capfd.readouterr().out == helper.generate_hook_out()

    def test_setup(self, capfd):
        helper.create_file(self.a_txt_backup, helper.random_str())
        helper.create_file(self.b1_txt_backup, helper.random_str())
        helper.create_file(self.b2_txt_backup, helper.random_str())

        dotbackup.main(["setup"])
        assert helper.dirdiff(self.a_config_dir, self.a_backup_dir)
        assert helper.dirdiff(self.b_config_dir, self.b_backup_dir)
        assert capfd.readouterr().out == helper.generate_hook_out("setup")

    def test_clean_backup(self):
        # backup files created here should be cleaned before backup
        helper.create_file(self.a_txt, helper.random_str())
        helper.create_file(self.a_legacy_txt_backup, helper.random_str())
        helper.create_file(self.b1_txt, helper.random_str())
        helper.create_file(self.b2_txt_backup, helper.random_str())

        dotbackup.main(["--clean"])
        assert helper.dirdiff(self.a_config_dir, self.a_backup_dir)
        assert helper.dirdiff(self.b_config_dir, self.b_backup_dir)

    def test_clean_setup(self):
        # config files created here should be cleaned before setup
        helper.create_file(self.a_txt_backup, helper.random_str())
        helper.create_file(self.a_legacy_txt, helper.random_str())
        helper.create_file(self.b1_txt_backup, helper.random_str())
        helper.create_file(self.b2_txt, helper.random_str())

        dotbackup.main(["setup", "--clean"])
        assert helper.dirdiff(self.a_config_dir, self.a_backup_dir)
        assert helper.dirdiff(self.b_config_dir, self.b_backup_dir)
