from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(os.getenv("VIDEOMCP_UPLOAD_DIR", ROOT / "uploads"))
OUTPUT_DIR = Path(os.getenv("VIDEOMCP_OUTPUT_DIR", ROOT / "output"))
STATIC_DIR = ROOT / "static"

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")

for folder in (UPLOAD_DIR, OUTPUT_DIR):
    folder.mkdir(parents=True, exist_ok=True)
