from collections import defaultdict, deque


def _adjacency(edges: list[tuple[str, str]]) -> dict[str, list[str]]:
    g: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        g[a].add(b)
        g[b].add(a)
    return {k: sorted(v) for k, v in g.items()}


def shortest_path(
    edges: list[tuple[str, str]], start: str, end: str
) -> list[tuple[str, str]] | None:
    """无向图 BFS 最短路，返回按途经顺序排列的边列表；同站为 []，不可达为 None。"""
    if start == end:
        return []
    g = _adjacency(edges)
    if start not in g or end not in g:
        return None
    parent: dict[str, str | None] = {start: None}
    q: deque[str] = deque([start])
    while q:
        cur = q.popleft()
        if cur == end:
            break
        for nxt in g[cur]:
            if nxt in parent:
                continue
            parent[nxt] = cur
            q.append(nxt)
    if end not in parent:
        return None
    nodes: list[str] = []
    cur: str | None = end
    while cur is not None:
        nodes.append(cur)
        cur = parent[cur]
    nodes.reverse()
    return list(zip(nodes, nodes[1:]))


def shortest_hops(edges: list[tuple[str, str]], start: str, end: str) -> int | None:
    """Undirected graph BFS hop count; None if unreachable."""
    path = shortest_path(edges, start, end)
    return None if path is None else len(path)
