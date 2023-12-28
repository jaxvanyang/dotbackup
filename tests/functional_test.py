import helper
import pytest

import dotbackup


@pytest.fixture(autouse=True)
def _prepare_test(monkeypatch):
    helper.prepare_test(monkeypatch)


def test_empty(capfd):
    helper.create_file(helper.CONFIG_FILE)
    with pytest.raises(SystemExit):
        dotbackup.main()
    captured = capfd.readouterr()
    assert "empty configuration" in captured.err


def test_complex_script(capfd):
    helper.cp(helper.get_config_path("complex_script.yml"), helper.CONFIG_FILE)

    dotbackup.main()
    assert capfd.readouterr().out == "hello world\nhello world\n"


class TestBasic:
    a_txt = f"{helper.CONFIG_DIR}/app_a/a.txt"
    b1_txt = f"{helper.CONFIG_DIR}/app_b/b1.txt"
    b2_txt = f"{helper.CONFIG_DIR}/app_b/b2.txt"
    a_txt_backup = f"{helper.BACKUP_DIR}/app_a/.config/app_a/a.txt"
    b1_txt_backup = f"{helper.BACKUP_DIR}/app_b/.config/app_b/b1.txt"
    b2_txt_backup = f"{helper.BACKUP_DIR}/app_b/.config/app_b/b2.txt"

    @pytest.fixture(autouse=True)
    def _prepare(self):
        helper.cp(helper.get_config_path("basic.yml"), helper.CONFIG_FILE)
        helper.mkdir(helper.BACKUP_DIR)

    def test_skip_backup(self, capfd):
        dotbackup.main()
        assert capfd.readouterr().err.count("this file backup skipped") == 3

    def test_skip_setup(self, capfd):
        dotbackup.main(["setup"])
        assert capfd.readouterr().err.count("this file setup skipped") == 3

    def test_backup(self, capfd):
        content = helper.random_str()
        helper.create_file(self.a_txt, content)
        helper.create_file(self.b1_txt, content)
        helper.create_file(self.b2_txt, content)

        dotbackup.main()
        assert (
            content
            == helper.read_file(self.a_txt_backup)
            == helper.read_file(self.b1_txt_backup)
            == helper.read_file(self.b2_txt_backup)
        )
        assert capfd.readouterr().out == helper.generate_hook_out()

    def test_setup(self, capfd):
        content = helper.random_str()
        helper.create_file(self.a_txt_backup, content)
        helper.create_file(self.b1_txt_backup, content)
        helper.create_file(self.b2_txt_backup, content)

        dotbackup.main(["setup"])
        assert (
            content
            == helper.read_file(self.a_txt)
            == helper.read_file(self.b1_txt)
            == helper.read_file(self.b2_txt)
        )
        assert capfd.readouterr().out == helper.generate_hook_out("setup")
