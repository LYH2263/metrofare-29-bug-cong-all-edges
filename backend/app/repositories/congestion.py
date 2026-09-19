import sqlite3

from app.modules.congestion_surcharge import edge_key


def _row_to_dict(r: sqlite3.Row) -> dict:
    return {"a": r["a"], "b": r["b"], "level": r["level"], "surcharge": r["surcharge"]}


def list_all(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT a, b, level, surcharge FROM congestion_edges ORDER BY a, b"
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_map(conn: sqlite3.Connection) -> dict[tuple[str, str], dict]:
    return {(r["a"], r["b"]): {"level": r["level"], "surcharge": r["surcharge"]} for r in conn.execute(
        "SELECT a, b, level, surcharge FROM congestion_edges"
    ).fetchall()}


def upsert(conn: sqlite3.Connection, a: str, b: str, level: str, surcharge: float) -> dict:
    """按边设置拥挤等级与加价（同边重复设置即覆盖）。"""
    x, y = edge_key(a, b)
    conn.execute(
        """
        INSERT INTO congestion_edges(a, b, level, surcharge) VALUES (?, ?, ?, ?)
        ON CONFLICT(a, b) DO UPDATE SET level=excluded.level, surcharge=excluded.surcharge
        """,
        (x, y, level, surcharge),
    )
    conn.commit()
    return {"a": x, "b": y, "level": level, "surcharge": round(float(surcharge), 2)}


def delete(conn: sqlite3.Connection, a: str, b: str) -> int:
    """按边清除拥挤，返回删除的行数。"""
    x, y = edge_key(a, b)
    cur = conn.execute("DELETE FROM congestion_edges WHERE a=? AND b=?", (x, y))
    conn.commit()
    return cur.rowcount
