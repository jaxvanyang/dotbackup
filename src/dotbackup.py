#!/usr/bin/env python3

import logging
import os
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from logging import Formatter, Logger, LogRecord
from pathlib import Path

from ruamel.yaml import YAML

__VERSION__ = "1.2.0"


class ColorFormatter(Formatter):
    def format(self, record: LogRecord) -> str:  # pragma: no cover
        template = "\x1b[%dm{}\x1b[00m"

        if record.levelno == logging.INFO:
            template %= 32
        elif record.levelno == logging.WARNING:
            template %= 33
        elif record.levelno == logging.ERROR:
            template %= 31
        elif record.levelno == logging.CRITICAL:
            template %= 91
        else:
            template %= 36

        return template.format(super().format(record))


def init_logger() -> Logger:
    """Initialize the logger and return it."""

    formatter = ColorFormatter("%(levelname)s: %(message)s")
    handler = logging.StreamHandler()
    logger = logging.getLogger(__name__)

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


class Config:
    """Configuration of dotbackup with helper functions."""

    _CONFIG_DIR = "~/.config/dotbackup"
    _DEFAULT_CONFIG_FILE = f"{_CONFIG_DIR}/dotbackup.yml"
    _YAML = YAML(typ="safe")
    _LOGGER = logging.getLogger(__name__)

    def __init__(self, config_dict) -> None:
        self._dict = dict(config_dict)

    def __repr__(self) -> str:  # pragma: no cover
        return repr(self._dict)

    def __eq__(self, other) -> bool:
        if type(self) is not type(other):
            return False

        return self._dict == other._dict

    @classmethod
    def fromfile(cls, file):
        """Return a new Config object based on the YAML configuration file."""

        with open(cls._normpath(file), encoding="utf-8") as f:
            config_dict = cls._YAML.load(f)

            if config_dict is None:
                raise RuntimeError(f"empty configuration: {file}")

        return cls(config_dict)

    @classmethod
    def parse_args(cls, args):
        """Return a new Config object based on the parsed CLI arguments."""

        cls._LOGGER.setLevel(args.log_level)

        if args.version:
            cls.print_version()
            sys.exit()

        if (
            args.config.endswith(".yml")
            or "/" in args.config
            or os.path.isfile(args.config)
        ):
            config_file = args.config
        else:
            config_file = f"{cls._CONFIG_DIR}/{args.config}.yml"

        config = cls.fromfile(config_file)

        if args.list:
            config._list_apps()
            sys.exit()

        if args.clean:
            config._dict["clean"] = True
        config._dict["selected_apps"] = list(args.app)

        return config

    @classmethod
    def _add_arguments(cls, parser, typ="backup") -> None:
        """Add backup or setup arguments to the parser."""

        assert typ in ("backup", "setup")

        parser.add_argument(
            "-c",
            "--config",
            default=cls._DEFAULT_CONFIG_FILE,
            help=f"Configuration file (default: {cls._DEFAULT_CONFIG_FILE}).",
        )
        parser.add_argument(
            "-l",
            "--list",
            action="store_true",
            help="List configured applications and exit.",
        )
        parser.add_argument(
            "-V",
            "--version",
            action="store_true",
            help="Print the version number of dotbackup and exit.",
        )
        parser.add_argument(
            "--clean",
            action="store_true",
            help=(
                f"Do clean {typ}, i.e., delete old "
                f"{'backup' if typ == 'backup' else 'configuration'} "
                f"files before {typ}."
            ),
        )
        parser.add_argument(
            "--log-level",
            default="INFO",
            choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
            help="Set the log level (default: INFO).",
        )
        parser.add_argument(
            "app",
            help="Application to be backed up (default: all applications).",
            nargs="*",
        )

    @classmethod
    def main_parser(cls):
        """Return argument parser for dotbackup.py."""

        parser = ArgumentParser(
            prog="dotbackup.py", description="YAML config based backup utility."
        )
        subparsers = parser.add_subparsers(
            title="subcommands",
            dest="command",
            help="Sub-command to be executed.",
        )
        backup_parser = subparsers.add_parser(
            "backup", help="Do backup based on the YAML configuration."
        )
        setup_parser = subparsers.add_parser(
            "setup", help="Do setup based on the YAML configuration."
        )

        cls._add_arguments(backup_parser)
        cls._add_arguments(setup_parser, typ="setup")

        return parser

    @classmethod
    def dotbackup_parser(cls):
        """Return argument parser for dotbackup."""

        parser = ArgumentParser(
            prog="dotbackup", description="Do backup based on the YAML configuration."
        )
        cls._add_arguments(parser)

        return parser

    @classmethod
    def dotsetup_parser(cls):
        """Return argument parser for dotsetup."""

        parser = ArgumentParser(
            prog="dotsetup", description="Do setup based on the YAML configuration."
        )
        cls._add_arguments(parser, typ="setup")

        return parser

    @staticmethod
    def print_version() -> None:
        """Print version information."""

        print(f"dotbackup {__VERSION__}")

    @staticmethod
    def _normpath(path):
        """Normalize path, expand user home directory, etc."""

        return os.path.normpath(os.path.expanduser(path))

    @property
    def _backup_dir(self):
        return self._dict["backup_dir"]

    @property
    def _clean(self):
        return self._dict.get("clean", False)

    @property
    def _apps_dict(self):
        return self._dict.get("apps", dict())

    @property
    def _selected_apps(self) -> list:
        """Return a list of selected applications.
        An empty list indicates all applications.
        """
        return self._dict["selected_apps"]

    def _safe_run_hooks(self, typ, hook_dict, app=None) -> None:
        if typ not in hook_dict:
            return

        hook_title = typ if app is None else f"{app} {typ}"

        for command in hook_dict[typ]:
            self._LOGGER.info(f"running {hook_title} hook in shell:\n{command}")
            try:
                subprocess.run(
                    "sh -s", shell=True, input=command, text=True, check=True
                )
            except subprocess.CalledProcessError:
                raise RuntimeError(f"command failed: {command}")

    def _delete_old(self, path: Path):
        """Delete old file safely."""

        if not path.exists():
            return

        self._LOGGER.info(f"found old {path}, deleting...")

        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def _check_apps(self) -> bool:
        """Check whether every selected app in the configured app list."""

        for app in self._selected_apps:
            if app not in self._apps_dict:
                self._LOGGER.error(f"application not configured: {app}")
                return False

        return True

    def _get_ignore(self, app_dict):
        """Return a combination of global and application ignore patterns."""

        global_ignore = self._dict.get("ignore", [])
        app_ignore = app_dict.get("ignore", [])

        return shutil.ignore_patterns(*global_ignore, *app_ignore)

    def _get_backup_file_path(self, file) -> Path:
        """Return the backup file path to the source file."""

        src_path = file if isinstance(file, Path) else Path(self._normpath(file))
        rel_path = src_path.relative_to(Path.home())
        return self._normpath(self._backup_dir) / rel_path

    def _backup_files(self, app, files, ignore) -> None:
        """Back up files of app except ignore files."""

        for file in files:
            src_path = Path(self._normpath(file))
            dest_path = self._get_backup_file_path(src_path)

            if self._clean:
                self._delete_old(dest_path)

            if not src_path.exists():
                self._LOGGER.warning(
                    f"file not found: {file}: skip backing up this file"
                )
                continue

            self._LOGGER.info(f"copying {file} to {dest_path}...")

            if src_path.is_dir():
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True, ignore=ignore)
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dest_path)

    def _setup_files(self, app, files, ignore) -> None:
        """Set up files of app except ignore files."""

        for file in files:
            dest_path = Path(self._normpath(file))
            src_path = self._get_backup_file_path(dest_path)

            if self._clean:
                self._delete_old(dest_path)

            if not src_path.exists():
                self._LOGGER.warning(
                    f"file not found: {src_path}: skip setting up this file"
                )
                continue

            self._LOGGER.info(f"copying {src_path} to {dest_path}...")

            if src_path.is_dir():
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True, ignore=ignore)
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dest_path)

    def _set_env(self) -> None:
        """Set environment variable."""
        os.environ["BACKUP_DIR"] = self._backup_dir

    def _list_apps(self) -> None:
        """List configured applications."""
        print("\n".join(self._apps_dict.keys()))

    def backup(self) -> int:
        """Do backup."""

        if not self._check_apps():
            return 1

        self._set_env()

        self._safe_run_hooks("pre_backup", self._dict)

        apps = self._selected_apps if self._selected_apps else self._apps_dict.keys()

        for app in apps:
            app_dict = self._apps_dict[app]

            self._LOGGER.info(f"doing {app} backup...")
            self._safe_run_hooks("pre_backup", app_dict, app=app)

            if "files" in app_dict:
                self._backup_files(app, app_dict["files"], self._get_ignore(app_dict))

            self._safe_run_hooks("post_backup", app_dict, app=app)

        self._safe_run_hooks("post_backup", self._dict)

        return 0

    def setup(self) -> int:
        """Do setup."""

        if not self._check_apps():
            return 1

        self._set_env()

        self._safe_run_hooks("pre_setup", self._dict)

        apps = self._selected_apps if self._selected_apps else self._apps_dict.keys()

        for app in apps:
            app_dict = self._apps_dict[app]

            self._LOGGER.info(f"doing {app} setup...")
            self._safe_run_hooks("pre_setup", app_dict, app=app)

            if "files" in app_dict:
                self._setup_files(app, app_dict["files"], self._get_ignore(app_dict))

            self._safe_run_hooks("post_setup", app_dict, app=app)

        self._safe_run_hooks("post_setup", self._dict)

        return 0


def dotbackup(args=None) -> int:
    """The dotbackup CLI"""

    logger = init_logger()

    if args is None:
        args = sys.argv[1:]

    parser = Config.dotbackup_parser()
    args = parser.parse_args(args)

    try:
        return Config.parse_args(args).backup()
    except RuntimeError as e:
        logger.error(" ".join(e.args))
        return 1


def dotsetup(args=None) -> int:
    """The dotsetup CLI"""

    logger = init_logger()

    if args is None:
        args = sys.argv[1:]

    parser = Config.dotsetup_parser()
    args = parser.parse_args(args)

    try:
        return Config.parse_args(args).setup()
    except RuntimeError as e:
        logger.error(" ".join(e.args))
        return 1


def main(args=None):
    """The dotbackup.py CLI"""

    logger = init_logger()

    if args is None:
        args = sys.argv[1:]

    parser = Config.main_parser()
    args = parser.parse_args(args)

    if not args.command:
        parser.print_help()
        return 1

    try:
        config = Config.parse_args(args)
    except RuntimeError as e:
        logger.error(" ".join(e.args))
        return 1

    if args.command == "backup":
        return config.backup()
    else:
        return config.setup()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
