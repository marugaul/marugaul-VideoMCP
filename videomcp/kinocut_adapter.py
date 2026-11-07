from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class KinocutError(RuntimeError):
    pass


def kinocut_available() -> bool:
    return bool(shutil.which("kino"))


def doctor() -> dict:
    kino = shutil.which("kino")
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    return {
        "kinocut": bool(kino),
        "kinocut_path": kino,
        "ffmpeg": bool(ffmpeg),
        "ffprobe": bool(ffprobe),
    }


def run_kinocut(args: list[str], cwd: Path | None = None) -> str:
    kino = shutil.which("kino")
    if not kino:
        raise KinocutError("Kinocut no está instalado.")
    result = subprocess.run(
        [kino, *args],
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise KinocutError(result.stderr.strip() or result.stdout.strip() or "Kinocut falló")
    return result.stdout.strip()
