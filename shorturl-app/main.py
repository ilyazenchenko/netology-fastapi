from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import sqlite3, string, random, os, uvicorn

# DB_PATH = "/app/data/shorturl.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "shorturl.db")


app = FastAPI(title="Short URL Service")

class UrlIn(BaseModel):
    url: str

def get_conn():
    return sqlite3.connect(DB_PATH)

def gen_id(n=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

@app.on_event("startup")
def startup():
    print("STARTUP")
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            short_id TEXT PRIMARY KEY,
            full_url TEXT NOT NULL
        )
        """)

@app.get("/")
def root():
    return {"message": "URL shortener"}

@app.get("/debug")
def debug():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM urls").fetchall()
        return [{"short_id": r[0], "full_url": r[1]} for r in rows]

@app.post("/shorten")
def shorten(data: UrlIn):
    short_id = gen_id()
    full_url = data.url
    if not full_url.startswith(("http://", "https://")):
        full_url = "https://" + full_url  # добавляем протокол по умолчанию
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO urls (short_id, full_url) VALUES (?, ?)",
            (short_id, full_url)
        )
        conn.commit()
    return {"short_url": f"/{short_id}", "short_id": short_id}


@app.get("/stats/{short_id}")
def stats(short_id: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT full_url FROM urls WHERE short_id=?",
            (short_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404)
        return {"short_id": short_id, "full_url": row[0]}

@app.get("/{short_id}")
def redirect(short_id: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT full_url FROM urls WHERE short_id=?",
            (short_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404)
        return RedirectResponse(row[0])


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)