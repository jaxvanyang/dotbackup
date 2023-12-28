# dotbackup

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dotbackup)
[![PyPI - Version](https://img.shields.io/pypi/v/dotbackup)](https://pypi.org/project/dotbackup)
[![AUR version](https://img.shields.io/aur/version/dotbackup)](https://aur.archlinux.org/packages/dotbackup)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Lint: flake8](https://img.shields.io/badge/lint-flake8-blueviolet)](https://github.com/PyCQA/flake8)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1)](https://pycqa.github.io/isort)
[![Test: pytest](https://img.shields.io/badge/test-pytest-orange)](https://pytest.org)
[![Codecov](https://codecov.io/gh/jaxvanyang/dotbackup/graph/badge.svg)](https://codecov.io/gh/jaxvanyang/dotbackup)

YAML config based backup utility. Easy to use yet flexible. With a primary focus on
dotfile backup & setup, but not limited to dotfiles.

## Features

- Simple configuration.
- Custom hooks.

## Installation

You can download [the script](./src/dotbackup.py) and place it to somewhere you like:

```bash
curl -L -o ~/.local/bin/dotbackup \
    "https://github.com/jaxvanyang/dotbackup/raw/main/src/dotbackup.py"
chmod +x ~/.local/bin/dotbackup
```

Or you can install from one of these package managers:

- [PyPI](https://pypi.org/project/dotbackup)
- [AUR](https://aur.archlinux.org/packages/dotbackup)

## Configuration

The default configuration file path is `~/.config/dotbackup/dotbackup.yml`, however you can
use the `-c` option to specify another configuration file. Configuration files use YAML
syntax. If you are new to YAML and want to learn more, see [Learn yaml in Y Minutes](https://learnxinyminutes.com/docs/yaml).
If you want a quick start, you can take [this](./examples/dotbackup.yml) as an example.
Following are the configuration keyword definitions, undefined keywords are ignored
(maybe I'll write a validator someday).

### `backup_dir`

Required. The directory where backup files store.

Example:

```yaml
backup_dir: ~/dotfiles
```

### `apps.<app>.files`

Optional. The files to be backed up of the application `<app>`, `<app>` can be any
string. File paths MUST be under the `$HOME` directory due to implementation. You can
use [custom hooks](#appsapppre_backuppost_backuppre_setuppost_setup) to back up other
files.

Example:

```yaml
apps:
  nvim:
    files:
      - ~/.config/nvim/init.lua
      - ~/.config/nvim/lua
```

### `apps.<app>.<pre_backup|post_backup|pre_setup|post_setup>`

Optional. The hooks to be executed before/after `<app>` backup/setup, `<app>` can be any
string. Each hook accept a list of commands, command are passed to `sh -c`. You can use
these hooks to do advance operation.

Example:

> FIXME: defining `BACKUP_DIR` is not implemented yet.

```yaml
apps:
  dotbackup:
    pre_backup:
      - cp /etc/dotbackup/dotbackup.yml "$BACKUP_DIR/dotbackup/dotbackup.yml"
    post_backup:
      - cd "$BACKUP_DIR" && git add dotbackup
    pre_setup:
      - pip install --user dotbackup || true
    post_setup:
      - sudo cp "$BACKUP_DIR/dotbackup/dotbackup.yml" /etc/dotbackup/dotbackup.yml
```

### `<pre_backup|post_backup|pre_setup|post_setup>`

Optional. The hooks to be executed before/after all backup/setup. Each hook accept a
list of commands, command are passed to `sh -c`. You can use these hooks to do advance
operation.

Example:

> FIXME: defining `BACKUP_DIR` is not implemented yet.

```yaml
pre_backup:
  - date > "$BACKUP_DIR/backup_date.txt"
post_backup:
  - |
    cd "$BACKUP_DIR"
    git add backup_date.txt
    git commit -m "update backups"
    git push
pre_setup:
  - cd "$BACKUP_DIR" && git pull
post_setup:
  - paru -Syu base-devel
```

## Usage

Some examples:

```bash
dotbackup nvim tmux
dotbackup backup nvim tmux
dotbackup setup nvim tmux
dotbackup setup
```

Run `dotbackup -h` for more information.
