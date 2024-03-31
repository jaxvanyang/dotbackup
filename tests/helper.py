import filecmp
import logging
import os
import random
import shutil
import string
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path

from dotbackup import Config

TEST_CONFIG_DIR = f"{os.path.dirname(__file__)}/configs"
TEST_HOME = ".dotbackup_test"
CONFIG_DIR = f"{TEST_HOME}/.config/dotbackup"
CONFIG_FILE = f"{CONFIG_DIR}/dotbackup.yml"
BACKUP_DIR = f"{TEST_HOME}/backup"

# not use monkeypatch because that may break modification to os.environ,
# i.e., setting env BACKUP_DIR would fail
os.environ["HOME"] = TEST_HOME


def clean_test(monkeypatch) -> None:
    """Set up clean environment for test."""

    monkeypatch.setattr(sys, "argv", sys.argv[:0])

    if os.path.isdir(TEST_HOME):
        shutil.rmtree(TEST_HOME)


def get_config_path(name) -> str:
    """Return path of test YAML configuration.

    Keyword arguments:
    name -- the YAML configuration name
    """

    return f"{TEST_CONFIG_DIR}/{name}.yml"


def get_config(name) -> Config:
    """Return a Config object of the test YAML configuration.

    Keyword arguments:
    name -- the YAML configuration name
    """

    return Config.fromfile(get_config_path(name))


def random_str(length=0) -> str:
    """Return a random string which is not empty."""
    length = length or random.randint(1, 50)
    return "".join(random.choices(string.ascii_uppercase, k=length))


def cp(src, dst):
    """Copy src to dst, create parent directories if necessary."""

    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)


def file_iterator(config: Config) -> Iterator:
    """Iterate files in the config."""

    for _, app_dict in config._apps_dict.items():
        if "files" not in app_dict:
            continue

        for file in app_dict["files"]:
            yield file


def backup_file_iterator(config: Config) -> Iterator:
    """Iterate backup files of the config."""

    return map(lambda f: str(config._get_backup_file_path(f)), file_iterator(config))


def create_file(path: str, content="") -> None:
    """Create a file in path with the content."""

    path = Config._normpath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode="w") as fp:
        fp.write(content)


def filediff(f1: str, f2: str) -> bool:
    """Return True if f1 and f2 are identical, False otherwise."""
    f1 = Config._normpath(f1)
    f2 = Config._normpath(f2)
    assert os.path.isfile(f1)
    assert os.path.isfile(f2)

    return filecmp.cmp(f1, f2, shallow=False)


def dirdiff(dir1: str, dir2: str, recursive=True) -> bool:
    """Return True if dir1 and dir2 seem identical, False otherwise."""

    def recursive_check(dcmp) -> bool:
        if any([dcmp.left_only, dcmp.right_only, dcmp.diff_files]):
            return False
        for sub_dcmp in dcmp.subdirs.values():
            if not recursive_check(sub_dcmp):
                return False
        return True

    dir1 = Config._normpath(dir1)
    dir2 = Config._normpath(dir2)
    assert os.path.isdir(dir1)
    assert os.path.isdir(dir2)

    dcmp = filecmp.dircmp(dir1, dir2)
    if not recursive:
        return not any([dcmp.left_only, dcmp.right_only, dcmp.diff_files])

    return recursive_check(dcmp)


def validate(files1: Iterable, files2: Iterable, recursive=True) -> bool:
    """Validate the backup or setup.

    Return True if each existing file in files1 is identical to coresponding file in
    files2, False otherwise."""

    files1 = map(lambda f: Config._normpath(f), files1)
    files2 = map(lambda f: Config._normpath(f), files2)
    for f1, f2 in zip(files1, files2):
        if not os.path.exists(f1):
            continue

        if (os.path.isfile(f1) and not filediff(f1, f2)) or (
            os.path.isdir(f1) and not dirdiff(f1, f2, recursive)
        ):
            logging.debug(f"{f1} and {f2} differ")
            return False

    return True


def validate_backup(config: Config, recursive=True) -> bool:
    return validate(file_iterator(config), backup_file_iterator(config), recursive)


def validate_setup(config: Config, recursive=True) -> bool:
    return validate(backup_file_iterator(config), file_iterator(config), recursive)


def rmdir(path: str) -> None:
    """Remove directory in path if it exists, i.e., rm -rf."""

    path = Config._normpath(path)
    if not os.path.isdir(path):
        return
    shutil.rmtree(path)


def mkdir(path: str) -> None:
    """Create directory in path, i.e., mkdir -p."""

    Path(Config._normpath(path)).mkdir(parents=True, exist_ok=True)
