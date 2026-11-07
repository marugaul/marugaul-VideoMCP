from __future__ import annotations

import uuid
from pathlib import Path

import httpx
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from .assets import search_pexels
from .auth import ALLOWED_EMAIL, SESSION_SECRET, verify_login
from .comfyui import health as comfy_health
from .config import OUTPUT_DIR, STATIC_DIR, UPLOAD_DIR
from .ffmpeg_engine import VideoError, render_reel

app = FastAPI(title="VideoMCP Studio", version="0.3.0")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET or "CHANGE-ME-BEFORE-PRODUCTION",
    same_site="lax",
    https_only=False,
)


class LoginRequest(BaseModel):
    email: str
    password: str


class SearchRequest(BaseModel):
    query: str
    kind: str = "photos"


class RenderRequest(BaseModel):
    files: list[str]
    music: str | None = None
    seconds_per_image: float = 2.5


def logged_in(request: Request) -> bool:
    return request.session.get("user") == ALLOWED_EMAIL


def require_login(request: Request):
    if not logged_in(request):
        raise HTTPException(status_code=401, detail="Autenticación requerida")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if logged_in(request):
        return RedirectResponse("/")
    return (STATIC_DIR / "login.html").read_text(encoding="utf-8")


@app.post("/api/login")
async def login(req: LoginRequest, request: Request):
    if not verify_login(req.email, req.password):
        raise HTTPException(401, "Correo o clave incorrectos")
    request.session.clear()
    request.session["user"] = ALLOWED_EMAIL
    return {"ok": True, "email": ALLOWED_EMAIL}


@app.post("/api/logout")
async def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if not logged_in(request):
        return RedirectResponse("/login")
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/api/health")
async def health(request: Request):
    require_login(request)
    return {"ok": True, "comfyui": await comfy_health()}


@app.post("/api/upload")
async def upload(request: Request, files: list[UploadFile] = File(...)):
    require_login(request)
    saved = []
    for f in files:
        suffix = Path(f.filename or "file").suffix
        name = f"{uuid.uuid4().hex}{suffix}"
        target = UPLOAD_DIR / name
        target.write_bytes(await f.read())
        saved.append({"name": name, "original": f.filename})
    return {"files": saved}


@app.post("/api/search")
async def search(req: SearchRequest, request: Request):
    require_login(request)
    results = await search_pexels(req.query, req.kind)
    return {
        "results": results,
        "configured": bool(results),
        "note": None if results else "Configura PEXELS_API_KEY para habilitar búsqueda gratuita."
    }


@app.post("/api/import-url")
async def import_url(request: Request, url: str = Form(...)):
    require_login(request)
    suffix = Path(url.split("?")[0]).suffix or ".bin"
    name = f"{uuid.uuid4().hex}{suffix}"
    target = UPLOAD_DIR / name
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        target.write_bytes(r.content)
    return {"name": name}


@app.post("/api/render")
async def render(req: RenderRequest, request: Request):
    require_login(request)
    try:
        media = [UPLOAD_DIR / Path(x).name for x in req.files]
        for p in media:
            if not p.exists():
                raise HTTPException(404, f"No existe {p.name}")

        music = UPLOAD_DIR / Path(req.music).name if req.music else None
        output = OUTPUT_DIR / f"reel-{uuid.uuid4().hex[:10]}.mp4"
        render_reel(media, output, req.seconds_per_image, music=music)
        return {"file": output.name, "url": f"/media/{output.name}"}
    except VideoError as e:
        raise HTTPException(500, str(e))


@app.get("/media/{filename}")
async def media(filename: str, request: Request):
    require_login(request)
    target = OUTPUT_DIR / Path(filename).name
    if not target.exists():
        raise HTTPException(404, "Archivo no encontrado")
    return FileResponse(target, media_type="video/mp4", filename=target.name)


def main():
    import uvicorn
    if not SESSION_SECRET:
        print("ADVERTENCIA: ejecutá 'videomcp-set-password' y configura .env antes de exponer la app.")
    uvicorn.run("videomcp.app:app", host="127.0.0.1", port=8000, reload=True)
