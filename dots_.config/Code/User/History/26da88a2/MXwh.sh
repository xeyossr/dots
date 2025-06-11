#!/bin/bash
set -e

DOTFILES_DIR="."  # Run from dotfiles root

CONFIG_DIR="$DOTFILES_DIR/dots_.config"
LOCAL_DIR="$DOTFILES_DIR/dots_.local"
ETC_DIR="$DOTFILES_DIR/dots_etc"
USR_DIR="$DOTFILES_DIR/dots_usr"
PKGS_DIR="$DOTFILES_DIR/dots_pkgs"
HOME_DIR="$DOTFILES_DIR/dots_home"

usage() {
    echo "Usage: $0 --backup | --install"
    exit 1
}

#copy_with_path() {
#    SRC="$1"
#    DEST_BASE="$2"
#
#    if [ -e "$SRC" ]; then
#        REL_PATH="$SRC"
        # Normalize REL_PATH for known prefixes
#        if [[ "$SRC" == "$HOME/.config/"* ]]; then
#            REL_PATH="${SRC#"$HOME"/.config/}"
#        elif [[ "$SRC" == "$HOME/.local/"* ]]; then
#            REL_PATH="${SRC#"$HOME"/.local/}"
#        elif [[ "$SRC" == "/etc/"* ]]; then
#            REL_PATH="${SRC#"/etc/"}"
#        elif [[ "$SRC" == "/usr/"* ]]; then
#            REL_PATH="${SRC#"/usr/"}"
#        else
#            REL_PATH="$(basename "$SRC")"
#        fi
#
#        DEST="$DEST_BASE/$REL_PATH"
#        mkdir -p "$(dirname "$DEST")"
#        cp -r "$SRC" "$DEST"
#        echo "✅ Copied: $SRC → $DEST"
#    else
#        echo "⚠️ Skipped (not found): $SRC"
#    fi
#}

sync_with_path() {
    SRC="$1"
    DEST_BASE="$2"

    if [ -e "$SRC" ]; then
        if [[ "$SRC" == "$HOME/.config/"* ]]; then
            REL_PATH="${SRC#"$HOME/.config/"}"
        elif [[ "$SRC" == "$HOME/.local/"* ]]; then
            REL_PATH="${SRC#"$HOME/.local/"}"
        elif [[ "$SRC" == "/etc/"* ]]; then
            REL_PATH="${SRC#"/etc/"}"
        elif [[ "$SRC" == "/usr/"* ]]; then
            REL_PATH="${SRC#"/usr/"}"
        else
            REL_PATH="$(basename "$SRC")"
        fi

        DEST="$DEST_BASE/$REL_PATH"

        mkdir -p "$(dirname "$DEST")"

        # rsync çıktı verirse farklılık var demektir
        if rsync -arc --delete "$SRC/" "$DEST/" | grep -q .; then
            echo "✅ Synced: $SRC → $DEST"
        fi
        # eğer rsync çıktı vermezse yani hiçbir dosya kopyalanmazsa mesaj yok
    else
        echo "⚠️ Skipped (not found): $SRC"
    fi
}

install_packages() {
    echo "📦 Installing pacman packages..."
    if [ -f "$PKGS_DIR/pacman-pkgs.txt" ]; then
        sudo pacman -S --needed - < "$PKGS_DIR/pacman-pkgs.txt"
    else
        echo "⚠️ $PKGS_DIR/pacman-pkgs.txt not found, skipping pacman packages install."
    fi

    echo "📦 Installing AUR packages with yay..."
    if [ -f "$PKGS_DIR/aur-pkgs.txt" ]; then
        yay -S --needed - < "$PKGS_DIR/aur-pkgs.txt"
    else
        echo "⚠️ $PKGS_DIR/aur-pkgs.txt not found, skipping AUR packages install."
    fi
}

install_dotfiles() {
    echo "📂 Installing dotfiles..."

    # Copy configs back
    if [ -d "$CONFIG_DIR" ]; then
        cp -r "$CONFIG_DIR/." "$HOME/.config/"
        echo "✅ Restored config files to ~/.config/"
    else
        echo "⚠️ $CONFIG_DIR not found, skipping config restore."
    fi

    # Copy local files back
    if [ -d "$LOCAL_DIR" ]; then
        cp -r "$LOCAL_DIR/bin" "$HOME/.local/"
        cp -r "$LOCAL_DIR/lib" "$HOME/.local/"
        cp -r "$LOCAL_DIR/share" "$HOME/.local/"
        cp -r "$LOCAL_DIR/state" "$HOME/.local/"
        echo "✅ Restored local files to ~/.local/"
    else
        echo "⚠️ $LOCAL_DIR not found, skipping local restore."
    fi

    # Copy etc back (may need sudo)
    if [ -d "$ETC_DIR" ]; then
        sudo cp -r "$ETC_DIR/." /etc/
        echo "✅ Restored /etc files"
    else
        echo "⚠️ $ETC_DIR not found, skipping /etc restore."
    fi

    # Copy usr back (may need sudo)
    if [ -d "$USR_DIR" ]; then
        sudo cp -r "$USR_DIR/." /usr/
        echo "✅ Restored /usr files"
    else
        echo "⚠️ $USR_DIR not found, skipping /usr restore."
    fi

    # Copy home dotfiles back
    if [ -d "$HOME_DIR" ]; then
        for file in aliases gitconfig; do
            if [ -f "$HOME_DIR/.$file" ]; then
                cp "$HOME_DIR/.$file" "$HOME/.$file"
                echo "✅ Restored $file to ~/"
            else
                echo "$HOME_DIR/.$file not found, skipping."
            fi
        done
    else
        echo "⚠️ $HOME_DIR not found, skipping home dotfiles restore."
    fi
}

backup_dotfiles() {
    echo "📦 Starting fresh dotfiles backup..."

    #echo "🧹 Removing previous backups..."
    #rm -rf "$CONFIG_DIR" "$LOCAL_DIR" "$ETC_DIR" "$USR_DIR" "$PKGS_DIR" "$HOME_DIR"

    echo "🛠 Recreate directory structure..."
    mkdir -p "$CONFIG_DIR" "$LOCAL_DIR/bin" "$LOCAL_DIR/lib" "$LOCAL_DIR/share" "$LOCAL_DIR/state"
    mkdir -p "$ETC_DIR" "$USR_DIR/share/plymouth/themes"
    mkdir -p "$PKGS_DIR"
    mkdir -p "$HOME_DIR"

    echo "📂 Copying from ~/.config..."
    for path in \
        fastfetch swayosd fish vim gtk-3.0 hypr hyde kitty Kvantum lsd menus nwg-look \
        qt5ct qt6ct rofi starship swaylock systemd/user tmux waybar wlogout xsettingsd \
        Code/User; do
        sync_with_path "$HOME/.config/$path" "$CONFIG_DIR"
    done

    for file in \
        baloofilerc code-flags.conf dolphinrc kdeglobals spotify-flags.conf; do
        sync_with_path "$HOME/.config/$file" "$CONFIG_DIR"
    done

    echo "📂 Copying from ~/.local..."
    for bin in hyde-ipc hyde-shell hydectl; do
        sync_with_path "$HOME/.local/bin/$bin" "$LOCAL_DIR"
    done

    sync_with_path "$HOME/.local/lib/hyde" "$LOCAL_DIR"

    for share in fastfetch waybar hyde icons kio kxmlgui5; do
        sync_with_path "$HOME/.local/share/$share" "$LOCAL_DIR"
    done

    for state in hyde dolphinstaterc .staterc; do
        sync_with_path "$HOME/.local/state/$state" "$LOCAL_DIR"
    done

    echo "📂 Copying from /etc (sudo)..."
    sync_with_path "/etc/plymouth" "$ETC_DIR"

    echo "📂 Copying from /usr (sudo)..."
    sync_with_path "/usr/share/plymouth/themes/spinner" "$USR_DIR"

    echo "📂 Copying home dotfiles (~/.aliases, ~/.gitconfig)..."
    for file in aliases gitconfig; do
        if [ -f "$HOME/.$file" ]; then
            cp "$HOME/.$file" "$HOME_DIR/.$file"
            echo "✅ Copied: $HOME/.$file → $HOME_DIR/.$file"
        else
            echo "⚠️ Skipped (not found): $HOME/.$file"
        fi
    done

    echo "📦 Saving package lists..."
    pacman -Qqe > "$PKGS_DIR/pacman-pkgs.txt"
    yay -Qm | awk '{print $1}' > "$PKGS_DIR/aur-pkgs.txt"
    echo "✅ Package lists saved to $PKGS_DIR"

    echo "🎉 Dotfiles backup completed (fresh state)!"
}

if [ "$#" -ne 1 ]; then
    usage
fi

case "$1" in
    --backup)
        backup_dotfiles
        ;;
    --install)
        install_packages
        install_dotfiles
        echo "🎉 Dotfiles installation completed!"
        ;;
    *)
        usage
        ;;
esac
