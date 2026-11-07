from __future__ import annotations

import httpx
from .config import PEXELS_API_KEY


async def search_pexels(query: str, kind: str = "photos", per_page: int = 12) -> list[dict]:
    if not PEXELS_API_KEY:
        return []

    headers = {"Authorization": PEXELS_API_KEY}
    async with httpx.AsyncClient(timeout=30) as client:
        if kind == "videos":
            r = await client.get(
                "https://api.pexels.com/videos/search",
                params={"query": query, "per_page": per_page, "orientation": "portrait"},
                headers=headers,
            )
            r.raise_for_status()
            data = r.json()
            out = []
            for item in data.get("videos", []):
                files = sorted(item.get("video_files", []), key=lambda x: x.get("width", 0))
                url = files[-1]["link"] if files else None
                if url:
                    out.append({
                        "id": item["id"],
                        "type": "video",
                        "preview": item.get("image"),
                        "url": url,
                        "source": "Pexels",
                    })
            return out

        r = await client.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": per_page, "orientation": "portrait"},
            headers=headers,
        )
        r.raise_for_status()
        return [{
            "id": p["id"],
            "type": "photo",
            "preview": p["src"]["medium"],
            "url": p["src"]["large2x"],
            "source": "Pexels",
            "photographer": p.get("photographer"),
        } for p in r.json().get("photos", [])]
