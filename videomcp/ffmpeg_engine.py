from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


class VideoError(RuntimeError):
    pass


def _bin(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise VideoError(f"{name} no está instalado o no está en PATH")
    return path


def probe(path: Path) -> str:
    result = subprocess.run(
        [_bin("ffprobe"), "-v", "error", "-show_entries",
         "format=duration:stream=codec_name,width,height", "-of", "default=nw=1", str(path)],
        text=True, capture_output=True
    )
    if result.returncode:
        raise VideoError(result.stderr.strip())
    return result.stdout.strip()


def render_reel(
    media: list[Path],
    output: Path,
    seconds_per_image: float = 2.5,
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
    music: Path | None = None,
) -> Path:
    if not media:
        raise VideoError("Se necesita al menos una imagen o video.")

    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="videomcp-"))
    normalized: list[Path] = []

    try:
        for i, src in enumerate(media):
            ext = src.suffix.lower()
            target = tmp / f"scene-{i:03d}.mp4"
            if ext in {".jpg", ".jpeg", ".png", ".webp"}:
                cmd = [
                    _bin("ffmpeg"), "-y", "-loop", "1", "-i", str(src),
                    "-t", str(seconds_per_image),
                    "-vf",
                    f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                    f"crop={width}:{height},"
                    "zoompan=z='min(zoom+0.0006,1.06)':"
                    "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                    f"d={int(seconds_per_image*fps)}:s={width}x{height}:fps={fps},"
                    "format=yuv420p",
                    "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(target)
                ]
            else:
                cmd = [
                    _bin("ffmpeg"), "-y", "-i", str(src),
                    "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps={fps},format=yuv420p",
                    "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(target)
                ]
            result = subprocess.run(cmd, text=True, capture_output=True)
            if result.returncode:
                raise VideoError(result.stderr[-2000:])
            normalized.append(target)

        manifest = tmp / "concat.txt"
        manifest.write_text("\n".join(f"file '{p.as_posix()}'" for p in normalized), encoding="utf-8")
        silent = tmp / "silent.mp4"
        result = subprocess.run([
            _bin("ffmpeg"), "-y", "-f", "concat", "-safe", "0", "-i", str(manifest),
            "-c", "copy", str(silent)
        ], text=True, capture_output=True)
        if result.returncode:
            raise VideoError(result.stderr[-2000:])

        if music:
            result = subprocess.run([
                _bin("ffmpeg"), "-y", "-i", str(silent), "-stream_loop", "-1", "-i", str(music),
                "-map", "0:v:0", "-map", "1:a:0", "-shortest",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(output)
            ], text=True, capture_output=True)
        else:
            result = subprocess.run([
                _bin("ffmpeg"), "-y", "-i", str(silent), "-c", "copy", "-movflags", "+faststart", str(output)
            ], text=True, capture_output=True)

        if result.returncode:
            raise VideoError(result.stderr[-2000:])
        return output
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
