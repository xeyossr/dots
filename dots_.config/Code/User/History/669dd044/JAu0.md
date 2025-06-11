![dotfiles](pr/dotfiles.png)

# Dependencies

| Type          | Package(s)       |
| ------------- | ---------------- |
| WM            | `hyprland`       |
| Bar           | `waybar`         |
| Launcher      | `rofi`           |
| Notifications | `dunst`/`swaync` |
| Terminal      | `kitty`          |
| Shell         | `fish`           |

You can use `yay -S --needed - < dots_pkgs/aur-pkgs.txt && sudo pacman -S --needed - < dots_pkgs/pacman-pkgs.txt` to install all dependencies.
To install all dotfiles, you need to use `./dotfiles.sh --install`.

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
