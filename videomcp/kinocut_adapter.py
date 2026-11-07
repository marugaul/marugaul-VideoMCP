from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from kinocut import Client


class KinocutError(RuntimeError):
    pass


def doctor() -> dict:
    return {
        "kinocut_cli": bool(shutil.which("kino")),
        "kinocut_cli_path": shutil.which("kino"),
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "ffprobe": bool(shutil.which("ffprobe")),
    }


def _client() -> Client:
    try:
        return Client()
    except Exception as exc:
        raise KinocutError(f"No se pudo iniciar Kinocut: {exc}") from exc


def inspect_tool(name: str) -> Any:
    return _client().inspect(name)


def edit_pipeline(
    source: str,
    output: str,
    text: str | None = None,
    aspect_ratio: str = "9:16",
    normalize_audio: bool = True,
) -> dict:
    ops: list[dict] = []
    if text:
        ops.append({"op": "add_text", "text": text, "position": "bottom-center"})
    if normalize_audio:
        ops.append({"op": "normalize_audio"})
    ops.extend([
        {"op": "resize", "aspect_ratio": aspect_ratio},
        {"op": "export", "quality": "high"},
        {"op": "release_checkpoint"},
    ])
    try:
        result = _client().pipeline(
            [{"op": "trim", "input": str(source), "start": "00:00:00"}, *ops],
            output_path=str(output),
        )
        return {"output": str(output), "result": result}
    except Exception as exc:
        raise KinocutError(str(exc)) from exc


def release_checkpoint(path: str) -> Any:
    try:
        return _client().release_checkpoint(str(path))
    except Exception as exc:
        raise KinocutError(str(exc)) from exc


def resize(path: str, output: str, aspect_ratio: str = "9:16") -> Any:
    try:
        result = _client().resize(str(path), aspect_ratio=aspect_ratio, output_path=str(output))
        return result
    except TypeError:
        result = _client().resize(str(path), aspect_ratio=aspect_ratio)
        produced = getattr(result, "output_path", None)
        if produced and Path(produced) != Path(output):
            shutil.copy2(produced, output)
        return result
    except Exception as exc:
        raise KinocutError(str(exc)) from exc
