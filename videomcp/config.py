from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
APP_HOME = Path(os.getenv("VIDEOMCP_HOME", Path.home() / ".videomcp"))
load_dotenv(APP_HOME / ".env")
load_dotenv(ROOT / ".env", override=False)

UPLOAD_DIR = Path(os.getenv("VIDEOMCP_UPLOAD_DIR", APP_HOME / "uploads"))
OUTPUT_DIR = Path(os.getenv("VIDEOMCP_OUTPUT_DIR", APP_HOME / "output"))
STATIC_DIR = ROOT / "static"
WORKFLOW_DIR = ROOT / "workflows"

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")

for folder in (APP_HOME, UPLOAD_DIR, OUTPUT_DIR):
    folder.mkdir(parents=True, exist_ok=True)
