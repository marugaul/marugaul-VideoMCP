from __future__ import annotations

import asyncio
import sys

from .comfyui import health as comfy_health
from .kinocut_adapter import doctor as kinocut_doctor


def main():
    editor = kinocut_doctor()
    comfy = asyncio.run(comfy_health())

    print("VideoMCP Doctor")
    print("================")
    print(f"Kinocut CLI : {'OK' if editor['kinocut_cli'] else 'FALTA'}")
    print(f"FFmpeg      : {'OK' if editor['ffmpeg'] else 'FALTA'}")
    print(f"ffprobe     : {'OK' if editor['ffprobe'] else 'FALTA'}")
    print(f"ComfyUI     : {'OK' if comfy['available'] else 'OPCIONAL / NO INICIADO'}")

    required_ok = editor["kinocut_cli"] and editor["ffmpeg"] and editor["ffprobe"]
    raise SystemExit(0 if required_ok else 1)


if __name__ == "__main__":
    main()
