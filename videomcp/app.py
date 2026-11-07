from __future__ import annotations

import uuid
from pathlib import Path

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from .assets import search_pexels
from .comfyui import health as comfy_health, queue_workflow
from .config import OUTPUT_DIR, STATIC_DIR, UPLOAD_DIR
from .ffmpeg_engine import VideoError, render_reel
from .kinocut_adapter import KinocutError, doctor as kinocut_doctor, release_checkpoint

app = FastAPI(title="VideoMCP Studio", version="0.4.0")


class SearchRequest(BaseModel):
    query: str
    kind: str = "photos"


class RenderRequest(BaseModel):
    files: list[str]
    music: str | None = None
    seconds_per_image: float = 2.5
    quality_check: bool = True


class WorkflowRequest(BaseModel):
    workflow: dict


@app.get("/", response_class=HTMLResponse)
async def home():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/api/health")
async def health():
    return {
        "ok": True,
        "kinocut": kinocut_doctor(),
        "comfyui": await comfy_health(),
    }


@app.post("/api/upload")
async def upload(files: list[UploadFile] = File(...)):
    saved = []
    for f in files:
        suffix = Path(f.filename or "file").suffix.lower()
        name = f"{uuid.uuid4().hex}{suffix}"
        target = UPLOAD_DIR / name
        target.write_bytes(await f.read())
        saved.append({"name": name, "original": f.filename})
    return {"files": saved}


@app.post("/api/search")
async def search(req: SearchRequest):
    results = await search_pexels(req.query, req.kind)
    return {
        "results": results,
        "configured": bool(results),
        "note": None if results else "Agregá PEXELS_API_KEY al archivo ~/.videomcp/.env para habilitar búsqueda gratuita."
    }


@app.post("/api/import-url")
async def import_url(url: str = Form(...)):
    suffix = Path(url.split("?")[0]).suffix.lower() or ".bin"
    name = f"{uuid.uuid4().hex}{suffix}"
    target = UPLOAD_DIR / name
    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        target.write_bytes(r.content)
    return {"name": name}


@app.post("/api/comfyui/workflow")
async def comfyui_workflow(req: WorkflowRequest):
    status = await comfy_health()
    if not status["available"]:
        raise HTTPException(503, "ComfyUI no está iniciado.")
    return await queue_workflow(req.workflow)


@app.post("/api/render")
async def render(req: RenderRequest):
    try:
        media = [UPLOAD_DIR / Path(x).name for x in req.files]
        for p in media:
            if not p.exists():
                raise HTTPException(404, f"No existe {p.name}")

        music = UPLOAD_DIR / Path(req.music).name if req.music else None
        output = OUTPUT_DIR / f"reel-{uuid.uuid4().hex[:10]}.mp4"

        # Stage 1: deterministic assembly/render through FFmpeg.
        render_reel(media, output, req.seconds_per_image, music=music)

        # Stage 2: Kinocut quality/release gate.
        checkpoint = None
        if req.quality_check:
            try:
                checkpoint = release_checkpoint(str(output))
            except KinocutError as exc:
                checkpoint = {"warning": str(exc)}

        return {
            "file": output.name,
            "url": f"/media/{output.name}",
            "checkpoint": checkpoint,
            "pipeline": "MCP -> Kinocut -> FFmpeg -> MP4",
        }
    except VideoError as exc:
        raise HTTPException(500, str(exc))


@app.get("/media/{filename}")
async def media(filename: str):
    target = OUTPUT_DIR / Path(filename).name
    if not target.exists():
        raise HTTPException(404, "Archivo no encontrado")
    return FileResponse(target, media_type="video/mp4", filename=target.name)


def main():
    import uvicorn
    uvicorn.run("videomcp.app:app", host="127.0.0.1", port=8000, reload=False)
