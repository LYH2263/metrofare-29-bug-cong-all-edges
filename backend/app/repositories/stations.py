import sqlite3


def list_all(conn: sqlite3.Connection) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT * FROM stations ORDER BY code").fetchall()]


def get_by_code(conn: sqlite3.Connection, code: str) -> dict | None:
    row = conn.execute("SELECT * FROM stations WHERE code=?", (code,)).fetchone()
    return dict(row) if row else None
