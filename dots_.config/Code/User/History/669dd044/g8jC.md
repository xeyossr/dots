![dotfiles](pr/dotfiles.png)

# Dependencies

| Type           | Package(s)                        |
| -------------- | --------------------------------- |
| OS             | Arch Linux                        |
| WM             | `hyprland`                        |
| Bar            | `waybar`                          |
| Launcher       | `rofi`                            |
| Notifications  | `swaync` / `dunst`                |
| Terminal       | `kitty`                           |
| Shell          | `fish`                            |
| Browser        | `brave`                           |
| Discord Client | `vencord` (custom instance)       |
| OSD            | `swayosd`                         |
| Floating TUI   | `pyprland` (e.g. for scratchpads) |
| GTK Theme      | `Catppuccin Mocha`                |
| Icon Theme     | `Tela Circle Dracula`             |
| Cursor Theme   | `macOS`-style (Bibata variant)    |

You can use `yay -S --needed - < dots_pkgs/aur-pkgs.txt && sudo pacman -S --needed - < dots_pkgs/pacman-pkgs.txt` to install all dependencies.  
To install all dotfiles, run `./dotfiles.sh --install`.

# Some shortcuts

| Shortcut               | Action                             |
| ---------------------- | ---------------------------------- |
| Super + Return (enter) | Launch floating terminal (`kitty`) |
| Super + E              | Launch file manager (`dolphin`)    |
| Super + W              | Launch web browser (`brave`)       |
| Super + Shift + Q      | Close focused application          |
| Super + A / Space      | Start program launcher (`rofi`)    |
| Super + 1-9            | Switch workspaces from 1 to 9      |

## Screenshots

![hyprland](pr/1.png)
![hyprland](pr/2.png)
