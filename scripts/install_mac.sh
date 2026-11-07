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
echo "        VideoMCP Studio - Mac Installer"
echo "============================================"
echo ""

mkdir -p "$APP_HOME" "$LOG_DIR" "$LAUNCH_DIR"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew no está instalado."
  echo "Instálalo desde https://brew.sh y vuelve a ejecutar este instalador."
  exit 1
fi

echo "[1/7] Dependencias del sistema"
brew list ffmpeg >/dev/null 2>&1 || brew install ffmpeg
brew list python@3.12 >/dev/null 2>&1 || brew install python@3.12
brew list git >/dev/null 2>&1 || brew install git

PYTHON="$(brew --prefix python@3.12)/bin/python3.12"

echo "[2/7] VideoMCP"
if [ -d "$REPO_DIR/.git" ]; then
  git -C "$REPO_DIR" pull --ff-only
else
  rm -rf "$REPO_DIR"
  git clone "$REPO_URL" "$REPO_DIR"
fi

echo "[3/7] Entorno Python"
"$PYTHON" -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip wheel
"$VENV/bin/pip" install -e "$REPO_DIR"

echo "[4/7] Kinocut"
"$VENV/bin/pip" install "kinocut>=1.16.5,<2"

echo "[5/7] Configuración"
if [ ! -f "$APP_HOME/.env" ]; then
  cp "$REPO_DIR/.env.example" "$APP_HOME/.env"
fi

echo "[6/7] Inicio automático"
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
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>$LOG_DIR/web.out.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/web.err.log</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST" >/dev/null 2>&1 || true
launchctl load "$PLIST"

echo "[7/7] Validación"
"$VENV/bin/python" - <<'PY'
import shutil
print("FFmpeg:", shutil.which("ffmpeg") or "NO")
print("Kinocut:", shutil.which("kino") or "NO")
PY

echo ""
echo "Instalación lista."
echo "VideoMCP Web: http://127.0.0.1:8000"
echo "MCP command: $VENV/bin/videomcp-mcp"
echo "ComfyUI/Wan es opcional y se configura después."
echo ""
