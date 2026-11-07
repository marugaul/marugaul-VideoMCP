from __future__ import annotations

from pathlib import Path
from mcp.server import MCPServer

from .assets import search_pexels
from .comfyui import health as comfy_health, queue_workflow
from .config import OUTPUT_DIR, UPLOAD_DIR
from .ffmpeg_engine import probe, render_reel
from .kinocut_adapter import (
    doctor as kinocut_doctor,
    inspect_tool,
    release_checkpoint,
)

mcp = MCPServer("VideoMCP Studio")


@mcp.tool()
def estado_sistema() -> dict:
    """Verifica Kinocut, FFmpeg y rutas locales de VideoMCP."""
    return {
        "editor": kinocut_doctor(),
        "uploads": str(UPLOAD_DIR),
        "outputs": str(OUTPUT_DIR),
    }


@mcp.tool()
def listar_archivos() -> list[str]:
    """Lista fotos, videos y audios locales disponibles para crear un video."""
    return sorted(p.name for p in UPLOAD_DIR.iterdir() if p.is_file())


@mcp.tool()
def inspeccionar_media(nombre: str) -> str:
    """Obtiene información técnica de una foto, audio o video local."""
    return probe(UPLOAD_DIR / Path(nombre).name)


@mcp.tool()
def descubrir_herramienta_kinocut(nombre: str) -> object:
    """Consulta el esquema de una operación de Kinocut antes de usarla."""
    return inspect_tool(nombre)


@mcp.tool()
async def buscar_recursos(query: str, tipo: str = "photos") -> list[dict]:
    """Busca fotos o videos verticales gratuitos con el proveedor configurado."""
    return await search_pexels(query, tipo)


@mcp.tool()
async def estado_comfyui() -> dict:
    """Indica si ComfyUI está listo para generación local."""
    return await comfy_health()


@mcp.tool()
async def generar_con_comfyui(workflow: dict) -> dict:
    """Envía un workflow de ComfyUI/Wan al generador local."""
    return await queue_workflow(workflow)


@mcp.tool()
def crear_reel(
    archivos: list[str],
    salida: str = "reel.mp4",
    segundos_por_imagen: float = 2.5,
    musica: str | None = None,
    control_calidad: bool = True,
) -> dict:
    """Crea un Reel vertical y pasa la salida por el checkpoint de Kinocut."""
    media = [UPLOAD_DIR / Path(x).name for x in archivos]
    for path in media:
        if not path.exists():
            raise FileNotFoundError(path)

    music = UPLOAD_DIR / Path(musica).name if musica else None
    output = OUTPUT_DIR / Path(salida).name

    # FFmpeg is the renderer underneath the VideoMCP assembly.
    render_reel(media, output, segundos_por_imagen, music=music)

    checkpoint = None
    if control_calidad:
        try:
            checkpoint = release_checkpoint(str(output))
        except Exception as exc:
            checkpoint = {"warning": str(exc)}

    return {
        "output": str(output),
        "checkpoint": checkpoint,
        "flow": "ChatGPT/agent -> MCP -> Kinocut -> FFmpeg -> MP4",
    }


def main():
    mcp.run()


if __name__ == "__main__":
    main()
