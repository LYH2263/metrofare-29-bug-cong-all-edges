from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import shortest_path
from app.modules.congestion_surcharge import surcharge_along_path


def quote_route(
    edges: list[tuple[str, str]],
    start: str,
    end: str,
    rules: list[dict],
    congestion: dict[tuple[str, str], dict] | None = None,
) -> dict:
    path = shortest_path(edges, start, end)
    if path is None:
        return {
            "start": start,
            "end": end,
            "hops": None,
            "fare": None,
            "base_fare": None,
            "congestion_edges": [],
            "congestion_total": 0.0,
            "payable": None,
            "reachable": False,
        }
    hops = len(path)
    base_fare = fare_for_hops(hops, rules)
    congested, congestion_total = surcharge_along_path(path, congestion or {})
    payable = round(base_fare + congestion_total, 2)
    return {
        "start": start,
        "end": end,
        "hops": hops,
        "fare": payable,
        "base_fare": base_fare,
        "path_edges": [{"a": a, "b": b} for a, b in path],
        "congestion_edges": congested,
        "congestion_total": congestion_total,
        "payable": payable,
        "reachable": True,
    }
