from app.db import connect
from app.engines.route_quote import quote_route
from app.modules.congestion_surcharge import (
    CongestionError,
    edge_key,
    validate_level,
    validate_surcharge,
)
from app.repositories import congestion as congestion_repo
from app.repositories import edges as edges_repo
from app.repositories import fare_rules as rules_repo
from app.repositories import runs as runs_repo
from app.repositories import settings as settings_repo
from app.repositories import stations as stations_repo


class MetroService:
    def __init__(self):
        self._conn = connect()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def stations(self):
        return stations_repo.list_all(self._conn)

    def station(self, code: str):
        return stations_repo.get_by_code(self._conn, code)

    def edges(self):
        congestion = congestion_repo.get_map(self._conn)
        items = []
        for a, b in edges_repo.list_pairs(self._conn):
            info = congestion.get(edge_key(a, b))
            items.append(
                {
                    "a": a,
                    "b": b,
                    "level": info["level"] if info else None,
                    "surcharge": info["surcharge"] if info else None,
                }
            )
        return items

    def congestion_edges(self):
        return congestion_repo.list_all(self._conn)

    def set_congestion(self, a: str, b: str, level: str, surcharge):
        level = validate_level(level)
        amount = validate_surcharge(surcharge)
        if not edges_repo.exists(self._conn, a, b):
            raise CongestionError(f"边 {a}—{b} 不存在，不能设置拥挤附加")
        return congestion_repo.upsert(self._conn, a, b, level, amount)

    def clear_congestion(self, a: str, b: str):
        if not edges_repo.exists(self._conn, a, b):
            raise CongestionError(f"边 {a}—{b} 不存在，不能清除拥挤附加")
        # 只删当前拥挤设置；历史记录是写入当时的冻结快照，回读不得改动
        removed = congestion_repo.delete(self._conn, a, b)
        return {"a": a, "b": b, "removed": removed}

    def fare_rules(self):
        return rules_repo.list_ordered(self._conn)

    def settings(self):
        return settings_repo.get_map(self._conn)

    def quote(self, start: str, end: str, persist: bool):
        edges = edges_repo.list_pairs(self._conn)
        rules = rules_repo.as_calc_rules(self._conn)
        congestion = congestion_repo.get_map(self._conn)
        result = quote_route(edges, start, end, rules, congestion)
        run_id = None
        if persist and result.get("reachable"):
            run_id = runs_repo.insert(self._conn, "quote", {"start": start, "end": end}, result)
        return {"run_id": run_id, **result}

    def history(self, limit=50):
        return runs_repo.list_recent(self._conn, limit)

    def run(self, run_id: int):
        # 历史详情直接返回写入时的冻结快照（含当时途经拥挤边与附加合计），
        # 不用当前全图拥挤边覆盖，保证列表与合计一致、清边后旧记录不变
        return runs_repo.get_by_id(self._conn, run_id)

    def dashboard(self):
        st = stations_repo.list_all(self._conn)
        clean = [s for s in st if "种子" not in s["name"]]
        dirty = [s for s in st if "种子" in s["name"]]
        return {
            "station_count": len(st),
            "edge_count": len(edges_repo.list_pairs(self._conn)),
            "clean_stations": len(clean),
            "dirty_stations": len(dirty),
        }
