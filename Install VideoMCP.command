#!/bin/bash
set -e
TMP_DIR="$HOME/Downloads/VideoMCP-Installer"
rm -rf "$TMP_DIR"
git clone https://github.com/marugaul/marugaul-VideoMCP.git "$TMP_DIR"
cd "$TMP_DIR"
bash scripts/install_mac.sh
echo ""
echo "Instalación finalizada."
read -n 1 -s -r -p "Presioná cualquier tecla para cerrar..."
