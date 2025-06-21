#!/bin/bash

set -e

REPO="xeyossr/anitr-cli"
BINARY_NAME="anitr-cli"
TMP_PATH="/tmp/$BINARY_NAME"
INSTALL_PATH="/usr/bin/$BINARY_NAME"

echo "🔄 Yeni sürüm indiriliyor..."

LATEST_URL="https://github.com/$REPO/releases/latest/download/$BINARY_NAME"
wget -q -O "$TMP_PATH" "$LATEST_URL"

chmod +x "$TMP_PATH"

echo "📁 Kurulum dizinine yazılıyor..."

if [ "$EUID" -ne 0 ]; then
    sudo cp "$TMP_PATH" "$INSTALL_PATH"
else
    cp "$TMP_PATH" "$INSTALL_PATH"
fi

echo "✅ anitr-cli başarıyla güncellendi!"
