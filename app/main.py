from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
import os
import sqlite3
import json
from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field, ConfigDict

DB_PATH = os.getenv("DATABASE_PATH", "data/app.db")

def connect():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

@asynccontextmanager
async def lifespan(app):
    with connect() as db:
        db.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, payload TEXT NOT NULL)")
    yield

app = FastAPI(title='Records Analytics API', version="1.0.0", lifespan=lifespan)

class ItemInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=150)
    category: str = Field(min_length=1, max_length=80)
    status: Literal["pending", "reviewed", "completed"] = "pending"
    amount: float = Field(default=0, ge=0, allow_inf_nan=False)

class ItemOutput(ItemInput):
    id: int

def decode(row):
    return {"id": row["id"], **json.loads(row["payload"])}

def require(db, item_id):
    row = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Item not found")
    return decode(row)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/records/summary")
def summary():
    with connect() as db:
        rows = [decode(r) for r in db.execute("SELECT * FROM items")]
    statuses = {}
    for row in rows:
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1
    result = {"total": len(rows), "by_status": statuses}
    result["total_amount"] = round(sum(row["amount"] for row in rows), 2)
    categories = {}
    for row in rows:
        categories[row["category"]] = categories.get(row["category"], 0) + 1
    result["by_category"] = categories
    return result

@app.post("/records", response_model=ItemOutput, status_code=201)
def create(item: ItemInput):
    payload = item.model_dump()
    with connect() as db:
        cursor = db.execute("INSERT INTO items (payload) VALUES (?)", (json.dumps(payload),))
        return {"id": cursor.lastrowid, **payload}

@app.get("/records", response_model=list[ItemOutput])
def listing(status: str | None = None, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    with connect() as db:
        if status is None:
            rows = db.execute("SELECT * FROM items ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
        else:
            rows = db.execute("SELECT * FROM items WHERE json_extract(payload, '$.status') = ? ORDER BY id DESC LIMIT ? OFFSET ?", (status, limit, offset)).fetchall()
        return [decode(r) for r in rows]

@app.get("/records/{item_id}", response_model=ItemOutput)
def retrieve(item_id: int):
    with connect() as db:
        return require(db, item_id)

@app.put("/records/{item_id}", response_model=ItemOutput)
def replace(item_id: int, item: ItemInput):
    with connect() as db:
        require(db, item_id)
        db.execute("UPDATE items SET payload = ? WHERE id = ?", (json.dumps(item.model_dump()), item_id))
    return {"id": item_id, **item.model_dump()}

@app.delete("/records/{item_id}", status_code=204)
def delete(item_id: int):
    with connect() as db:
        require(db, item_id)
        db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    return Response(status_code=204)
