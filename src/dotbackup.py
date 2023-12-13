#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys
from argparse import ArgumentParser

from ruamel.yaml import YAML

__VERSION__ = "0.0.2"
ENCODING = "UTF-8"

HOME = os.path.abspath(os.environ["HOME"])
CONFIG_FILE = "~/.config/dotbackup/config.yml"


def eprint(msg):
    print(msg, file=sys.stderr)


def log(msg):
    eprint(f"\033[32mLOG:\033[00m {msg}")


def warn(msg):
    eprint(f"\033[33mWARN:\033[00m {msg}")


def error(msg):
    eprint(f"\033[31mERROR:\033[00m {msg}")
    sys.exit(1)


def run(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError:
        error(f"command failed: {command}")


def run_hooks(typ, hooks):
    for command in hooks:
        sh_command = f"sh -c '{command}'"
        log(f"running {typ} hook in shell: {sh_command}")
        run(sh_command)


def normfilepath(file_path):
    if file_path == "~":
        return HOME
    if file_path.startswith("~/"):
        return os.path.join(HOME, file_path.removeprefix("~/"))

    return os.path.normpath(file_path)


class App:
    def __init__(self, name, config):
        self.name = name
        self.files = config["files"] if "files" in config else []
        self.pre_backup = config["pre_backup"] if "pre_backup" in config else []
        self.post_backup = config["post_backup"] if "post_backup" in config else []
        self.pre_setup = config["pre_setup"] if "pre_setup" in config else []
        self.post_setup = config["post_setup"] if "post_setup" in config else []

    def backup(self, backup_dir):
        log(f"doing {self.name} backup...")

        if not os.path.isdir(backup_dir):
            error(f"backup directory not found: {backup_dir}")

        run_hooks(f"{self.name} pre-backup", self.pre_backup)

        for file in self.files:
            file_path = normfilepath(file)
            if not file_path.startswith(HOME):
                error(
                    f"file or directory not under {HOME}: {file_path}: you can use "
                    f"hooks to do backup for files not under the home directory"
                )

            relative_path = file_path.removeprefix(HOME)
            dst = os.path.normpath(f"{backup_dir}/{self.name}/{relative_path}")

            if os.path.isfile(file_path):
                log(f"copying {file_path} to {dst}...")
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(file_path, dst)
            elif os.path.isdir(file_path):
                log(f"copying {file_path} to {dst}...")
                shutil.copytree(file_path, dst, dirs_exist_ok=True)
            else:
                warn(f"file or directory not found: {file}: this file backup skipped")

        run_hooks(f"{self.name} post-backup", self.post_backup)

    def setup(self, backup_dir):
        log(f"doing {self.name} setup...")

        if not os.path.isdir(backup_dir):
            error(f"backup directory not found: {backup_dir}")

        run_hooks(f"{self.name} pre-setup", self.pre_setup)

        for file in self.files:
            file_path = normfilepath(file)
            if not file_path.startswith(HOME):
                error(
                    f"file or directory not under {HOME}: {file_path}: you can use "
                    f"hooks to do backup for files not under the home directory"
                )

            relative_path = file_path.removeprefix(HOME)
            src = os.path.normpath(f"{backup_dir}/{self.name}/{relative_path}")

            if os.path.isfile(src):
                log(f"copying {src} to {file_path}...")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                shutil.copy2(src, file_path)
            elif os.path.isdir(src):
                log(f"copying {src} to {file_path}...")
                shutil.copytree(src, file_path, dirs_exist_ok=True)
            else:
                warn(f"file or directory not found: {src}: this file setup skipped")

        run_hooks(f"{self.name} post-setup", self.post_setup)


class Config:
    def __init__(self, config_dict):
        if config_dict is None:
            error("empty configuration")

        if "backup_dir" not in config_dict:
            error("bad configuration: backup_dir is not set")

        self.backup_dir = normfilepath(config_dict["backup_dir"])
        self.pre_backup = (
            config_dict["pre_backup"] if "pre_backup" in config_dict else []
        )
        self.post_backup = (
            config_dict["post_backup"] if "post_backup" in config_dict else []
        )
        self.pre_setup = config_dict["pre_setup"] if "pre_setup" in config_dict else []
        self.post_setup = (
            config_dict["post_setup"] if "post_setup" in config_dict else []
        )
        self.apps = (
            [App(k, v) for (k, v) in config_dict["apps"].items()]
            if "apps" in config_dict
            else []
        )

    def backup(self):
        run_hooks("pre-backup", self.pre_backup)

        for app in self.apps:
            app.backup(self.backup_dir)

        run_hooks("post-backup", self.post_backup)

    def setup(self):
        run_hooks("pre-setup", self.pre_setup)

        for app in self.apps:
            app.setup(self.backup_dir)

        run_hooks("post-setup", self.post_setup)


def parse_args():
    parser = ArgumentParser(
        prog="dotbackup", description="YAML config based backup utility."
    )

    parser.add_argument(
        "-c",
        "--config",
        default=normfilepath(CONFIG_FILE),
        help=f"Configuration file (default: {CONFIG_FILE}).",
    )
    parser.add_argument(
        "command",
        help="Sub-command to be executed, backup or setup (default: backup).",
        nargs="?",
    )
    parser.add_argument(
        "apps",
        action="append",
        help=(
            "Applications to be backed up or set up. Omit this to back up or set up "
            "all applications."
        ),
        nargs="?",
    )

    return parser.parse_args()


def parse_config(config_file):
    if not os.path.isfile(config_file):
        error(f"configuration file not found: {config_file}")

    with open(config_file, encoding=ENCODING) as f:
        config_dict = YAML(typ="safe").load(f)

    return Config(config_dict)


def backup(config, apps):
    if apps[0] is None:
        config.backup()
        return

    app_dict = {app.name: app for app in config.apps}

    for app in apps:
        if app not in app_dict:
            error(f"application not configured: {app}")

    for app in apps:
        app_dict[app].backup(config.backup_dir)


def setup(config, apps):
    if apps[0] is None:
        config.setup()
        return

    app_dict = {app.name: app for app in config.apps}

    for app in apps:
        if app not in app_dict:
            error(f"application not configured: {app}")

    for app in apps:
        app_dict[app].setup(config.backup_dir)


def main():
    args = parse_args()
    apps = args.apps
    config = parse_config(normfilepath(args.config))

    match args.command:
        case "backup" | None:
            backup(config, apps)
        case "setup":
            setup(config, apps)
        case _:  # command argument is omitted
            if apps[0] is None:
                apps = [args.command]
            else:
                apps.insert(0, args.command)
            backup(config, apps)

    return 0


if __name__ == "__main__":
    sys.exit(main())
