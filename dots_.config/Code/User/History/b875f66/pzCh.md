# lastf

[![Latest Release](https://img.shields.io/github/release/xeyossr/lastf.svg?style=for-the-badge)](https://github.com/xeyossr/lastf/releases)
[![Software License](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](/LICENSE)

Better `last` command interface with structured output.

![lastf_long-date](/lastf_long-date.png)
![lastf](/lastf.png)

## Installation

### Packages

- Arch Linux: `yay -S lastf`

### From source

```bash
git clone https://github.com/xeyossr/lastf.git
cd lastf
chmod +x build.sh && ./build.sh
```

## Usage

You can simply start duf without any command-line arguments:

    duf

If you supply arguments, duf will only list specific devices & mount points:

    duf /home /some/file

If you want to list everything (including pseudo, duplicate, inaccessible file systems):

    duf --all
