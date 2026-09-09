"""SQLite 저장소 계층.

모든 DB 접근은 이 모듈을 통해서만 이루어지므로, 나중에 Supabase(PostgreSQL) 등으로
바꿀 때 이 파일만 교체하면 된다.
"""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _default_db_path() -> str:
    # Vercel 서버리스 환경은 /tmp 만 쓰기 가능
    if os.environ.get("VERCEL"):
        return "/tmp/todo.db"
    return os.path.join(BASE_DIR, "todo.db")


def get_db_path() -> str:
    return os.environ.get("TODO_DB_PATH") or _default_db_path()


@contextmanager
def _connect():
    """커밋 후 반드시 close 한다.

    sqlite3 의 기본 컨텍스트 매니저는 커밋/롤백만 하고 연결을 닫지 않아
    Windows 에서 파일 잠금이 남고, 서버리스에서는 연결이 누수된다.
    """
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                done       INTEGER NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL
            )
            """
        )


def _row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
        "created_at": row["created_at"],
    }


def list_todos(status: str = "all") -> list[dict]:
    """status: all | active | done"""
    where = {"active": "WHERE done = 0", "done": "WHERE done = 1"}.get(status, "")
    with _connect() as conn:
        rows = conn.execute(
            f"SELECT * FROM todos {where} ORDER BY done ASC, id DESC"
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def count_todos() -> dict:
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS total, "
            "SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) AS done FROM todos"
        ).fetchone()
    total = row["total"] or 0
    done = row["done"] or 0
    return {"total": total, "done": done, "active": total - done}


def get_todo(todo_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return _row_to_dict(row) if row else None


def add_todo(title: str) -> dict:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO todos (title, done, created_at) VALUES (?, 0, ?)",
            (title, created_at),
        )
        new_id = cur.lastrowid
    return get_todo(new_id)


def update_todo(todo_id: int, title: str | None = None, done: bool | None = None) -> dict | None:
    sets, params = [], []
    if title is not None:
        sets.append("title = ?")
        params.append(title)
    if done is not None:
        sets.append("done = ?")
        params.append(1 if done else 0)
    if not sets:
        return get_todo(todo_id)
    params.append(todo_id)
    with _connect() as conn:
        conn.execute(f"UPDATE todos SET {', '.join(sets)} WHERE id = ?", params)
    return get_todo(todo_id)


def toggle_todo(todo_id: int) -> dict | None:
    with _connect() as conn:
        conn.execute("UPDATE todos SET done = 1 - done WHERE id = ?", (todo_id,))
    return get_todo(todo_id)


def delete_todo(todo_id: int) -> bool:
    with _connect() as conn:
        cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    return cur.rowcount > 0


def clear_done() -> int:
    with _connect() as conn:
        cur = conn.execute("DELETE FROM todos WHERE done = 1")
    return cur.rowcount
