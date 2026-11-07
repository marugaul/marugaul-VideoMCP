from __future__ import annotations

from pathlib import Path
from mcp.server import MCPServer

from .assets import search_pexels
from .comfyui import health as comfy_health
from .config import OUTPUT_DIR, UPLOAD_DIR
from .ffmpeg_engine import probe, render_reel

mcp = MCPServer("VideoMCP Studio")


@mcp.tool()
def listar_archivos() -> list[str]:
    """Lista los archivos locales disponibles para crear un video."""
    return sorted(p.name for p in UPLOAD_DIR.iterdir() if p.is_file())


@mcp.tool()
def inspeccionar_media(nombre: str) -> str:
    """Obtiene información técnica de un archivo multimedia."""
    return probe(UPLOAD_DIR / Path(nombre).name)


@mcp.tool()
async def buscar_recursos(query: str, tipo: str = "photos") -> list[dict]:
    """Busca fotos o videos verticales mediante el proveedor gratuito configurado."""
    return await search_pexels(query, tipo)


@mcp.tool()
async def estado_generador_ia() -> dict:
    """Indica si ComfyUI está disponible para generar imágenes o clips localmente."""
    return await comfy_health()


@mcp.tool()
def crear_reel(
    archivos: list[str],
    salida: str = "reel.mp4",
    segundos_por_imagen: float = 2.5,
    musica: str | None = None,
) -> str:
    """Crea un Reel vertical 1080x1920 con FFmpeg."""
    media = [UPLOAD_DIR / Path(x).name for x in archivos]
    music = UPLOAD_DIR / Path(musica).name if musica else None
    output = OUTPUT_DIR / Path(salida).name
    render_reel(media, output, segundos_por_imagen, music=music)
    return str(output)


def main():
    mcp.run()
