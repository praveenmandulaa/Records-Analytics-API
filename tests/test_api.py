import pytest
from fastapi.testclient import TestClient
from app import main

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", str(tmp_path / "test.db"))
    with TestClient(main.app) as c:
        yield c

SAMPLE = {'title': 'Property record review', 'category': 'deeds', 'status': 'pending', 'amount': 2500}
BASE = "/records"

def test_crud_filter_summary(client):
    assert client.get(BASE + "/summary").json()["total"] == 0
    r = client.post(BASE, json=SAMPLE)
    assert r.status_code == 201
    item_id = r.json()["id"]
    assert client.get(f"{BASE}/{item_id}").json()["id"] == item_id
    assert len(client.get(BASE, params={"status": SAMPLE["status"]}).json()) == 1
    assert client.get(BASE, params={"offset": 1}).json() == []
    assert client.get(BASE + "/summary").json()["total"] == 1
    changed = {**SAMPLE, "status": "completed"}
    assert client.put(f"{BASE}/{item_id}", json=changed).json()["status"] == "completed"
    assert client.delete(f"{BASE}/{item_id}").status_code == 204
    assert client.get(f"{BASE}/{item_id}").status_code == 404

def test_validation_and_missing(client):
    assert client.post(BASE, json={}).status_code == 422
    assert client.post(BASE, json={**SAMPLE, "status": "invalid"}).status_code == 422
    assert client.get(BASE, params={"limit": 101}).status_code == 422
    assert client.put(BASE + "/999", json=SAMPLE).status_code == 404
    assert client.delete(BASE + "/999").status_code == 404

def test_persistence(client):
    client.post(BASE, json=SAMPLE)
    with main.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 1
