#!/bin/bash
set -euo pipefail

REPO_URL="https://github.com/marugaul/marugaul-VideoMCP.git"
APP_HOME="$HOME/.videomcp"
VENV="$APP_HOME/.venv"
REPO_DIR="$APP_HOME/app"
LOG_DIR="$APP_HOME/logs"
LAUNCH_DIR="$HOME/Library/LaunchAgents"
PLIST="$LAUNCH_DIR/com.marugaul.videomcp.web.plist"

echo ""
echo "============================================"
echo "       VideoMCP Studio - Instalador Mac"
echo "============================================"
echo ""

mkdir -p "$APP_HOME" "$LOG_DIR" "$LAUNCH_DIR"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew no está instalado."
  echo "Instalalo desde https://brew.sh y volvé a ejecutar:"
  echo "bash scripts/install_mac.sh"
  exit 1
fi

echo "[1/7] Instalando dependencias..."
brew list ffmpeg >/dev/null 2>&1 || brew install ffmpeg
brew list python@3.12 >/dev/null 2>&1 || brew install python@3.12
brew list git >/dev/null 2>&1 || brew install git

PYTHON="$(brew --prefix python@3.12)/bin/python3.12"

echo "[2/7] Instalando VideoMCP..."
if [ -d "$REPO_DIR/.git" ]; then
  git -C "$REPO_DIR" fetch origin main
  git -C "$REPO_DIR" reset --hard origin/main
else
  rm -rf "$REPO_DIR"
  git clone "$REPO_URL" "$REPO_DIR"
fi

echo "[3/7] Creando entorno Python..."
"$PYTHON" -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip wheel
"$VENV/bin/pip" install -e "$REPO_DIR"

echo "[4/7] Validando Kinocut + FFmpeg..."
"$VENV/bin/kino" doctor || true
"$VENV/bin/videomcp-doctor" || {
  echo "La validación principal falló. Revisá los mensajes anteriores."
  exit 1
}

echo "[5/7] Configuración local..."
if [ ! -f "$APP_HOME/.env" ]; then
  cp "$REPO_DIR/.env.example" "$APP_HOME/.env"
fi

echo "[6/7] Configurando arranque automático de la web..."
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.marugaul.videomcp.web</string>
  <key>ProgramArguments</key>
  <array>
    <string>$VENV/bin/videomcp-web</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$REPO_DIR</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>VIDEOMCP_HOME</key>
    <string>$APP_HOME</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$LOG_DIR/web.out.log</string>
  <key>StandardErrorPath</key><string>$LOG_DIR/web.err.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl kickstart -k "gui/$(id -u)/com.marugaul.videomcp.web"

echo "[7/7] Listo."
echo ""
echo "Web local : http://127.0.0.1:8000"
echo "MCP local : $VENV/bin/videomcp-mcp"
echo "Kinocut   : $VENV/bin/kino --mcp"
echo ""
echo "ComfyUI/Wan queda opcional. Para instalar ComfyUI:"
echo "bash $REPO_DIR/scripts/install_comfyui_mac.sh"
echo ""
open "http://127.0.0.1:8000" || true
