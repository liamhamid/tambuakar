"""Serving API (FastAPI) — dedah Gold read-only, bertoken.

Purpose: beri profil entiti (Gold) kepada Ajis & dashboard — read-only.
Responsibilities: baca gold/entities.jsonl, tapis/cari, sahkan token Bearer.
Dependencies: fastapi (lihat requirements.txt). Data dari fail Gold.
Future: Postgres; agregat (benchmark penajaan); rate-limit; bind Tailscale-only.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request


def load_entities(gold_dir: Path) -> list[dict]:
    path = gold_dir / "entities.jsonl"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def create_app(gold_dir: Path | None = None, token: str | None = None) -> FastAPI:
    resolved_dir = gold_dir or Path(os.environ.get("TAMBUAKAR_GOLD", "data/gold"))
    resolved_token = token if token is not None else os.environ.get("TAMBUAKAR_TOKEN", "")
    app = FastAPI(title="Tambuakar Serving API", version="0.1.0")

    def check_auth(authorization: str | None) -> None:
        # Token opsyenal untuk dev; WAJIB set TAMBUAKAR_TOKEN dalam prod (di sebalik
        # Tailscale). Bila diset, hanya "Bearer <token>" yang betul dibenarkan.
        if resolved_token and authorization != f"Bearer {resolved_token}":
            raise HTTPException(status_code=401, detail="unauthorized")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/entities")
    def entities(
        request: Request,
        kind: str | None = None,
        q: str | None = None,
        limit: int = 50,
    ) -> dict[str, object]:
        check_auth(request.headers.get("authorization"))
        items = load_entities(resolved_dir)
        if kind:
            items = [e for e in items if e.get("kind") == kind]
        if q:
            needle = q.lower()
            items = [e for e in items if needle in str(e.get("canonical_name", "")).lower()]
        capped = items[: max(0, min(limit, 500))]
        return {"count": len(capped), "entities": capped}

    @app.get("/entities/{entity_id:path}")
    def entity(entity_id: str, request: Request) -> dict:
        check_auth(request.headers.get("authorization"))
        for item in load_entities(resolved_dir):
            if item.get("entity_id") == entity_id:
                return item
        raise HTTPException(status_code=404, detail="not found")

    return app


app = create_app()
