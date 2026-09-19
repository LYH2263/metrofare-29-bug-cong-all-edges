import sqlite3

from app.modules.congestion_surcharge import edge_key


def list_pairs(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    return [(r["a"], r["b"]) for r in conn.execute("SELECT a,b FROM edges").fetchall()]


def exists(conn: sqlite3.Connection, a: str, b: str) -> bool:
    x, y = edge_key(a, b)
    row = conn.execute(
        "SELECT 1 FROM edges WHERE (a=? AND b=?) OR (a=? AND b=?) LIMIT 1",
        (x, y, y, x),
    ).fetchone()
    return row is not None
