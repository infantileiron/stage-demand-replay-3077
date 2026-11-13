"""Small parameterized repository. MySQL in Compose; SQLite is explicit local QA mode."""
import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from src.config.settings import settings

TABLES = ("datasets", "scenarios", "runs", "plans", "reports", "users", "audit", "schedules", "delivery_snapshots")
_lock = threading.Lock()

@contextmanager
def connection():
    if settings.database_url.startswith("sqlite:///"):
        db = sqlite3.connect(settings.database_url[10:], timeout=30)
        db.row_factory = sqlite3.Row
    else:
        import pymysql
        u = urlparse(settings.database_url)
        db = pymysql.connect(host=u.hostname, port=u.port or 3306, user=unquote(u.username or ""),
             password=unquote(u.password or ""), database=u.path.lstrip("/"), charset="utf8mb4",
             cursorclass=pymysql.cursors.DictCursor, connect_timeout=10)
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def execute(db, sql, params=()):
    cur = db.cursor()
    cur.execute(sql.replace("?", "%s") if not isinstance(db, sqlite3.Connection) else sql, params)
    return cur

def init_db():
    with _lock, connection() as db:
        auto = "INTEGER PRIMARY KEY AUTOINCREMENT" if isinstance(db, sqlite3.Connection) else "BIGINT PRIMARY KEY AUTO_INCREMENT"
        for table in TABLES:
            execute(db, f"CREATE TABLE IF NOT EXISTS {table} (id {auto}, natural_key VARCHAR(180) UNIQUE NOT NULL, payload LONGTEXT NOT NULL, created_at VARCHAR(40) NOT NULL)")

def unpack(row):
    return dict(json.loads(row["payload"]), id=row["id"], key=row["natural_key"], created_at=row["created_at"])

def list_rows(table):
    assert table in TABLES
    with connection() as db:
        return [unpack(r) for r in execute(db, f"SELECT * FROM {table} ORDER BY id DESC").fetchall()]

def get_row(table, ident):
    assert table in TABLES
    with connection() as db:
        row = execute(db, f"SELECT * FROM {table} WHERE id = ?", (ident,)).fetchone()
    if row is None:
        from fastapi import HTTPException
        raise HTTPException(404, "记录不存在")
    return unpack(row)

def insert_row(table, key, payload, preserve=False):
    assert table in TABLES
    with connection() as db:
        old = execute(db, f"SELECT * FROM {table} WHERE natural_key = ?", (key,)).fetchone()
        if old:
            if preserve: return unpack(old)
            from fastapi import HTTPException
            raise HTTPException(409, "名称已存在，请使用新名称")
        cur = execute(db, f"INSERT INTO {table}(natural_key,payload,created_at) VALUES (?,?,?)",
            (key, json.dumps(payload, ensure_ascii=False, allow_nan=False), datetime.now(timezone.utc).isoformat()))
        ident = cur.lastrowid
    return get_row(table, ident)

def update_row(table, ident, changes):
    assert table in TABLES
    # Read and write under a single connection; queue has a single consumer per stack.
    with connection() as db:
        old = execute(db, f"SELECT * FROM {table} WHERE id = ?", (ident,)).fetchone()
        if old is None:
            from fastapi import HTTPException
            raise HTTPException(404, "记录不存在")
        value = json.loads(old["payload"])
        value.update(changes)
        execute(db, f"UPDATE {table} SET payload=? WHERE id=?", (json.dumps(value, ensure_ascii=False, allow_nan=False), ident))
    return get_row(table, ident)
