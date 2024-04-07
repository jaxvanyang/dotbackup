# dotbackup

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dotbackup)
[![PyPI - Version](https://img.shields.io/pypi/v/dotbackup)](https://pypi.org/project/dotbackup)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/dotbackup)](https://pypi.org/project/dotbackup)
[![AUR version](https://img.shields.io/aur/version/dotbackup)](https://aur.archlinux.org/packages/dotbackup)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Lint: flake8](https://img.shields.io/badge/lint-flake8-blueviolet)](https://github.com/PyCQA/flake8)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1)](https://pycqa.github.io/isort)
[![Test: pytest](https://img.shields.io/badge/test-pytest-orange)](https://pytest.org)
[![Codecov](https://codecov.io/gh/jaxvanyang/dotbackup/graph/badge.svg)](https://codecov.io/gh/jaxvanyang/dotbackup)

Usually people maintain backup and setup scripts along with their dotfiles. But
these scripts always contain a lot of repeat codes, and writing them is not fun!
`dotbackup` and `dotsetup` are here to help.

With these two tools, you only need to write a simple configuration and they
will know how to back up and set up your dotfiles. You can read [dotbackup(1)](dotbackup.1.adoc)
and [dotsetup(1)](dotsetup.1.adoc) for details.

## Highlights

- Simple configuration.
- Custom hooks.
- Detailed logs.

## Installation

You can install from one of these package managers:

- [PyPI](https://pypi.org/project/dotbackup)
- [AUR](https://aur.archlinux.org/packages/dotbackup)

Installing from a package manager gives you the two commands - `dotbackup` and
`dotsetup`, and the manpages. But you can also download this single script:
[dotbackup.py](./src/dotbackup.py). In fact, `dotbackup` and `dotsetup` are just
shortcut commands of `dotbackup.py`, which means that `dotbackup` is equivalent
to `dotbackup.py backup` and `dotsetup` is equivalent to `dotbackup.py setup`.

## Quick Start

Write a simple configuration and place it to `~/.config/dotbackup/dotbackup.yml`:

```yml
backup_dir: ~/backup
apps:
  vim:
    files: [~/.vimrc]
  nvim:
    files:
      - ~/.config/nvim/init.lua
      - ~/.config/nvim/lua
```

Do backup:

```console
$ dotbackup
INFO: doing vim backup...
INFO: copying ~/.vimrc to /home/user/backup/.vimrc...
INFO: doing nvim backup...
INFO: copying ~/.config/nvim/init.lua to /home/user/backup/.config/nvim/init.lua...
INFO: copying ~/.config/nvim/lua to /home/user/backup/.config/nvim/lua...
```

Do setup:

```console
$ dotsetup
INFO: doing vim setup...
INFO: copying /home/user/backup/.vimrc to /home/user/.vimrc...
INFO: doing nvim setup...
INFO: copying /home/user/backup/.config/nvim/init.lua to /home/user/.config/nvim/init.lua...
INFO: copying /home/user/backup/.config/nvim/lua to /home/user/.config/nvim/lua...
```

## Documentation

For more information, please read [dotbackup(1)](dotbackup.1.adoc) and [dotsetup(1)](dotsetup.1.adoc).
