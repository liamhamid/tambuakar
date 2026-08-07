"""Ujian offline untuk Serving API (FastAPI TestClient) — tiada rangkaian."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from tambuakar.api import create_app
from tambuakar.gold import write_gold
from tambuakar.identity import resolve
from tambuakar.ports import Record


def _rec(source: str, sid: str, name: str) -> Record:
    return Record(source=source, source_id=sid, kind="football_club", name=name)


def _client(tmp_path: Path, token: str = "") -> TestClient:
    records = [
        _rec("wikidata", "Q1", "Manchester United F.C."),
        _rec("gdelt", "u1", "Manchester United"),
    ]
    entities, identity_map = resolve(records)
    write_gold(entities, identity_map, tmp_path / "gold")
    return TestClient(create_app(gold_dir=tmp_path / "gold", token=token))


def test_health(tmp_path: Path) -> None:
    assert _client(tmp_path).get("/health").json()["status"] == "ok"


def test_entities_merged_and_listed(tmp_path: Path) -> None:
    body = _client(tmp_path).get("/entities").json()
    assert body["count"] == 1  # dua sumber Man Utd -> satu entiti
    assert body["entities"][0]["kind"] == "football_club"


def test_entities_search_filter(tmp_path: Path) -> None:
    client = _client(tmp_path)
    assert client.get("/entities", params={"q": "manchester"}).json()["count"] == 1
    assert client.get("/entities", params={"q": "arsenal"}).json()["count"] == 0


def test_token_enforced_when_set(tmp_path: Path) -> None:
    client = _client(tmp_path, token="secret")
    assert client.get("/entities").status_code == 401
    ok = client.get("/entities", headers={"Authorization": "Bearer secret"})
    assert ok.status_code == 200
