from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

DB_PATH = "/app/data/todo.db"

app = FastAPI(title="ToDo Service")

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class Todo(TodoCreate):
    id: int

def get_conn():
    return sqlite3.connect(DB_PATH)

@app.on_event("startup")
def startup():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS todo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN NOT NULL
        )
        """)

@app.post("/items", response_model=Todo)
def create_item(item: TodoCreate):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO todo (title, description, completed) VALUES (?, ?, ?)",
            (item.title, item.description, item.completed)
        )
        return {**item.dict(), "id": cur.lastrowid}

@app.get("/items", response_model=List[Todo])
def get_items():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM todo").fetchall()
        return [Todo(id=r[0], title=r[1], description=r[2], completed=bool(r[3])) for r in rows]

@app.get("/items/{item_id}", response_model=Todo)
def get_item(item_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM todo WHERE id=?", (item_id,)).fetchone()
        if not row:
            raise HTTPException(404)
        return Todo(id=row[0], title=row[1], description=row[2], completed=bool(row[3]))

@app.put("/items/{item_id}", response_model=Todo)
def update_item(item_id: int, item: TodoCreate):
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE todo SET title=?, description=?, completed=? WHERE id=?",
            (item.title, item.description, item.completed, item_id)
        )
        if cur.rowcount == 0:
            raise HTTPException(404)
        return {**item.dict(), "id": item_id}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM todo WHERE id=?", (item_id,))
        if cur.rowcount == 0:
            raise HTTPException(404)
        return {"status": "deleted"}
