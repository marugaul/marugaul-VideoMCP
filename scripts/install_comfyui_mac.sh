#!/bin/bash
set -euo pipefail

APP_HOME="$HOME/.videomcp"
COMFY_DIR="$APP_HOME/comfyui"
VENV="$COMFY_DIR/.venv"

echo ""
echo "============================================"
echo "     ComfyUI local - Instalador opcional"
echo "============================================"
echo ""
echo "Este paso instala ComfyUI, pero NO descarga modelos Wan automáticamente."
echo "Los modelos de video son grandes y se instalarán por separado."
echo ""

if ! command -v git >/dev/null 2>&1; then
  echo "Falta git. Ejecutá primero el instalador principal de VideoMCP."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Falta Python."
  exit 1
fi

if [ -d "$COMFY_DIR/.git" ]; then
  git -C "$COMFY_DIR" pull --ff-only
else
  rm -rf "$COMFY_DIR"
  git clone https://github.com/comfyanonymous/ComfyUI.git "$COMFY_DIR"
fi

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip wheel
"$VENV/bin/pip" install -r "$COMFY_DIR/requirements.txt"

cat > "$APP_HOME/start-comfyui.sh" <<EOF
#!/bin/bash
cd "$COMFY_DIR"
exec "$VENV/bin/python" main.py --listen 127.0.0.1 --port 8188
EOF
chmod +x "$APP_HOME/start-comfyui.sh"

echo ""
echo "ComfyUI instalado."
echo "Para iniciarlo:"
echo "$APP_HOME/start-comfyui.sh"
echo ""
echo "Luego VideoMCP lo detectará en http://127.0.0.1:8188"
