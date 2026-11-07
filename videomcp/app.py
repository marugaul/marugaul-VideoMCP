from __future__ import annotations

import uuid
from pathlib import Path

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .assets import search_pexels
from .comfyui import health as comfy_health
from .config import OUTPUT_DIR, STATIC_DIR, UPLOAD_DIR
from .ffmpeg_engine import VideoError, render_reel

app = FastAPI(title="VideoMCP Studio", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")


class SearchRequest(BaseModel):
    query: str
    kind: str = "photos"


class RenderRequest(BaseModel):
    files: list[str]
    music: str | None = None
    seconds_per_image: float = 2.5


@app.get("/", response_class=HTMLResponse)
async def home():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/api/health")
async def health():
    return {"ok": True, "comfyui": await comfy_health()}


@app.post("/api/upload")
async def upload(files: list[UploadFile] = File(...)):
    saved = []
    for f in files:
        suffix = Path(f.filename or "file").suffix
        name = f"{uuid.uuid4().hex}{suffix}"
        target = UPLOAD_DIR / name
        target.write_bytes(await f.read())
        saved.append({"name": name, "original": f.filename, "path": str(target)})
    return {"files": saved}


@app.post("/api/search")
async def search(req: SearchRequest):
    results = await search_pexels(req.query, req.kind)
    return {
        "results": results,
        "configured": bool(results),
        "note": None if results else "Configura PEXELS_API_KEY para habilitar búsqueda gratuita."
    }


@app.post("/api/import-url")
async def import_url(url: str = Form(...)):
    suffix = Path(url.split("?")[0]).suffix or ".bin"
    name = f"{uuid.uuid4().hex}{suffix}"
    target = UPLOAD_DIR / name
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        target.write_bytes(r.content)
    return {"name": name, "path": str(target)}


@app.post("/api/render")
async def render(req: RenderRequest):
    try:
        media = [UPLOAD_DIR / Path(x).name for x in req.files]
        for p in media:
            if not p.exists():
                raise HTTPException(404, f"No existe {p.name}")

        music = UPLOAD_DIR / Path(req.music).name if req.music else None
        output = OUTPUT_DIR / f"reel-{uuid.uuid4().hex[:10]}.mp4"
        render_reel(media, output, req.seconds_per_image, music=music)
        return {"file": output.name, "url": f"/output/{output.name}"}
    except VideoError as e:
        raise HTTPException(500, str(e))


def main():
    import uvicorn
    uvicorn.run("videomcp.app:app", host="127.0.0.1", port=8000, reload=True)
