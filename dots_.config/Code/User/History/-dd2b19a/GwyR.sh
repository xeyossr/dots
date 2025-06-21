#!/usr/bin/env bash

set -euo pipefail

PROJECT_NAME="lastf"
VENV_DIR=".venv"
DIST_DIR="dist/$PROJECT_NAME"
INSTALL_DIR="/opt/lastfancy"
BIN_PATH="/usr/bin/lastfancy"

if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

if ! python -m nuitka --version &>/dev/null; then
    echo "[+] Installing Nuitka in virtual environment..."
    pip install -U pip
    pip install nuitka
else
    echo "[+] Nuitka already installed in venv."
fi

echo "[+] Compiling with Nuitka..."
python -m nuitka \
    --standalone \
    --enable-plugin=pylint-warnings \
    --lto=yes \
    --clang \
    --jobs=4 \
    "$PROJECT_NAME.py"

echo "[+] Moving build to /opt..."
sudo rm -rf "$INSTALL_DIR"
sudo mv "$DIST_DIR" "$INSTALL_DIR"

echo "[+] Creating launcher at /usr/bin/lastfancy..."
sudo tee "$BIN_PATH" > /dev/null <<EOF
#!/usr/bin/env bash
exec "$INSTALL_DIR/$PROJECT_NAME" "\$@"
EOF
sudo chmod +x "$BIN_PATH"

echo "[✓] Build and install complete. Run using: lastfancy"
