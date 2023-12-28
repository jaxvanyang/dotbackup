import os
import random
import shutil
import string
import sys

import dotbackup

TEST_CONFIG_DIR = f"{os.path.dirname(__file__)}/configs"
TEST_HOME = "/tmp/dotbackup_test"
CONFIG_DIR = f"{TEST_HOME}/.config"
CONFIG_FILE = f"{CONFIG_DIR}/dotbackup/dotbackup.yml"
BACKUP_DIR = f"{TEST_HOME}/backup"

BASIC_CONFIG_DICT = {
    "backup_dir": "~/backup",
    "apps": {
        "app_a": {
            "files": ["~/.config/app_a"],
            "pre_backup": ["echo app_a pre_backup"],
            "post_backup": ["echo app_a post_backup"],
            "pre_setup": ["echo app_a pre_setup"],
            "post_setup": ["echo app_a post_setup"],
        },
        "app_b": {
            "files": ["~/.config/app_b/b1.txt", "~/.config/app_b/b2.txt"],
            "pre_backup": ["echo app_b pre_backup"],
            "post_backup": ["echo app_b post_backup"],
            "pre_setup": ["echo app_b pre_setup"],
            "post_setup": ["echo app_b post_setup"],
        },
    },
    "pre_backup": ["echo pre_backup"],
    "post_backup": ["echo post_backup"],
    "pre_setup": ["echo pre_setup"],
    "post_setup": ["echo post_setup"],
}
BASIC_CONFIG = dotbackup.Config(BASIC_CONFIG_DICT)
ONLY_HOOKS_DICT = {
    "backup_dir": "~/backup",
    "apps": {
        "app_a": {
            "pre_backup": ["echo app_a pre_backup"],
            "post_backup": ["echo app_a post_backup"],
            "pre_setup": ["echo app_a pre_setup"],
            "post_setup": ["echo app_a post_setup"],
        },
        "app_b": {
            "pre_backup": ["echo app_b pre_backup"],
            "post_backup": ["echo app_b post_backup"],
            "pre_setup": ["echo app_b pre_setup"],
            "post_setup": ["echo app_b post_setup"],
        },
    },
    "pre_backup": ["echo pre_backup"],
    "post_backup": ["echo post_backup"],
    "pre_setup": ["echo pre_setup"],
    "post_setup": ["echo post_setup"],
}
ONLY_HOOKS_CONFIG = dotbackup.Config(ONLY_HOOKS_DICT)

APPS_CHOICE = [[], ["app_a"], ["app_b"], ["app_a", "app_b"], ["app_b", "app_a"]]
CONFIG_PATHS = ["basic.yml", "only_hooks.yml", "complex_script.yml"]


def rm_test_home():
    if not os.path.exists(TEST_HOME):
        return

    if os.path.isfile(TEST_HOME):
        os.unlink(TEST_HOME)

    shutil.rmtree(TEST_HOME)


def prepare_test(monkeypatch):
    monkeypatch.setattr(dotbackup, "HOME", TEST_HOME)
    monkeypatch.setattr(sys, "argv", sys.argv[:0])
    rm_test_home()


def get_config_path(path):
    test_config_path = f"{TEST_CONFIG_DIR}/{path}"

    if os.path.isfile(test_config_path):
        return test_config_path

    return path


def get_config(path):
    if path == "basic.yml":
        return BASIC_CONFIG
    elif path == "only_hooks.yml":
        return ONLY_HOOKS_CONFIG

    return dotbackup.parse_config(get_config_path(path))


def random_str(length=50):
    return "".join(random.choices(string.ascii_uppercase, k=length))


def cp(src, dst):
    if os.path.isfile(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    elif os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        raise FileNotFoundError(src)


def mkdir(path):
    os.makedirs(path, exist_ok=True)


def create_file(path, content=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode="w") as fp:
        fp.write(content)


def read_file(path):
    with open(path) as fp:
        return fp.read()


def generate_hook_out(command="backup", apps=[]):
    if apps == []:
        apps = ["app_a", "app_b"]

    out = f"pre_{command}\n"
    for app in apps:
        out += f"{app} pre_{command}\n{app} post_{command}\n"
    out += f"post_{command}\n"

    return out
