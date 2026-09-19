import sqlite3


def get_map(conn: sqlite3.Connection) -> dict[str, str]:
    return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}
