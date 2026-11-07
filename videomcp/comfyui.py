from __future__ import annotations

import httpx
from .config import COMFYUI_URL


async def health() -> dict:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{COMFYUI_URL}/system_stats")
            return {"available": r.status_code == 200, "url": COMFYUI_URL}
    except Exception:
        return {"available": False, "url": COMFYUI_URL}


async def queue_workflow(workflow: dict) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow})
        r.raise_for_status()
        return r.json()
