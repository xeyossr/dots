![dotfiles](pr/dotfiles.png)

# Dependencies

| Type           | Package(s)            |
| -------------- | --------------------- |
| OS             | Arch Linux            |
| WM             | `hyprland`            |
| Bar            | `waybar`              |
| Scratchpad     | `pyprland`            |
| Launcher       | `rofi`                |
| Notifications  | `swaync` / `dunst`    |
| OSD            | `swayosd`             |
| Terminal       | `kitty`               |
| Shell          | `fish`                |
| Browser        | `brave`               |
| Discord Client | `vencord`             |
| GTK Theme      | `Catppuccin Mocha`    |
| Icon Theme     | `Tela Circle Dracula` |
| Cursor Theme   | `macOS`               |

You can use `yay -S --needed - < dots_pkgs/aur-pkgs.txt && sudo pacman -S --needed - < dots_pkgs/pacman-pkgs.txt` to install all dependencies.  
To install all dotfiles, run `./dotfiles.sh --install`.

> [!WARNING]
> This script may cause some issues with your configuration. Make sure to take a snapshot before using it.

# Some shortcuts

| Shortcut                          | Action                   |
| --------------------------------- | ------------------------ |
| `Super + W`                       | Open browser `(Brave)`   |
| `Super + T`                       | Open terminal `(kitty)`  |
| `Super + D`                       | Open Discord `(Vencord)` |
| `Super + A` / `Super + Space`     | Application finder       |
| `Super + Shift + E`               | File finder              |
| `Super + Tab`                     | Window switcher          |
| `Shift + F11` / `Alt + Return`    | Toggle fullscreen        |
| `Super + L`                       | Lock screen              |
| `Alt + Ctrl + Delete`             | Logout menu              |
| `Super + Shift + Q` / `Alt + F4`  | Close focused window     |
| `Super + Delete`                  | Kill Hyprland session    |
| `Super + /` / `Super + Shift + K` | Keybindings hint         |

## Screenshots

![hyprland](pr/1.png)
![hyprland](pr/2.png)

## Related Repositories

- [🥢 waybar_modules](https://github.com/xeyossr/waybar_modules)
