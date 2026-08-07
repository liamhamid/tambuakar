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


_TOKEN = "secret"
_AUTH = {"Authorization": f"Bearer {_TOKEN}"}


def _client(tmp_path: Path, token: str = _TOKEN) -> TestClient:
    records = [
        _rec("wikidata", "Q1", "Manchester United F.C."),
        _rec("gdelt", "u1", "Manchester United"),
    ]
    entities, identity_map = resolve(records)
    write_gold(entities, identity_map, tmp_path / "gold")
    return TestClient(create_app(gold_dir=tmp_path / "gold", token=token))


def test_health_open(tmp_path: Path) -> None:
    assert _client(tmp_path).get("/health").json()["status"] == "ok"


def test_entities_merged_and_listed(tmp_path: Path) -> None:
    body = _client(tmp_path).get("/entities", headers=_AUTH).json()
    assert body["count"] == 1  # dua sumber Man Utd -> satu entiti
    assert body["entities"][0]["kind"] == "football_club"


def test_entities_search_filter(tmp_path: Path) -> None:
    client = _client(tmp_path)
    assert client.get("/entities", params={"q": "manchester"}, headers=_AUTH).json()["count"] == 1
    assert client.get("/entities", params={"q": "arsenal"}, headers=_AUTH).json()["count"] == 0


def test_token_enforced(tmp_path: Path) -> None:
    client = _client(tmp_path)
    assert client.get("/entities").status_code == 401  # tiada header
    assert client.get("/entities", headers=_AUTH).status_code == 200


def test_fail_closed_when_token_missing(tmp_path: Path) -> None:
    client = _client(tmp_path, token="")
    assert client.get("/entities").status_code == 503  # tak dikonfigur -> enggan
