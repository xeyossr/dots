![dotfiles](pr/dotfiles.png)

# Dependencies

| Type           | Package(s)            |
| -------------- | --------------------- |
| OS             | Arch Linux            |
| WM             | `hyprland`            |
| Bar            | `waybar`              |
| Launcher       | `rofi`                |
| Notifications  | `swaync` / `dunst`    |
| Terminal       | `kitty`               |
| Shell          | `fish`                |
| Browser        | `brave`               |
| Discord Client | `vencord`             |
| OSD            | `swayosd`             |
| Scratchpad     | `pyprland`            |
| GTK Theme      | `Catppuccin Mocha`    |
| Icon Theme     | `Tela Circle Dracula` |
| Cursor Theme   | `macOS`               |

You can use `yay -S --needed - < dots_pkgs/aur-pkgs.txt && sudo pacman -S --needed - < dots_pkgs/pacman-pkgs.txt` to install all dependencies.  
To install all dotfiles, run `./dotfiles.sh --install`.

# Some shortcuts

| Shortcut                         | Action                        |
| -------------------------------- | ----------------------------- |
| `Super + Shift + Q` / `Alt + F4` | Close focused window          |
| Super + Delete                   | Kill Hyprland session         |
| Super + U                        | Toggle floating               |
| Super + G                        | Toggle group                  |
| Shift + F11                      | Toggle fullscreen             |
| Alt + Return                     | Toggle fullscreen             |
| Super + L                        | Lock screen                   |
| Super + Shift + F                | Pin/unpin focused window      |
| Alt + Ctrl + Delete              | Logout menu                   |
| Alt + Control_R                  | Reload config & toggle Waybar |
| Super + Alt + C                  | Toggle custom Waybar mode     |
| Super + A / Space                | Application finder            |
| Super + Tab                      | Window switcher               |
| Super + Shift + E                | File finder                   |
| `Super + /` / Super + Shift + K  | Keybindings hint              |

## Screenshots

![hyprland](pr/1.png)
![hyprland](pr/2.png)
