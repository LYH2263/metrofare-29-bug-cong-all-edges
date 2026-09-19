"""拥挤附加模块（congestion_surcharge）。

附加费挂在邻接边上：每条边可设置一个拥挤等级与对应加价。询价时沿
最短路依次经过每一条边，把其中拥挤边的加价加总，与钟点无关。

等级取值固定为 light / heavy / severe，加价必须为非负有限金额。边是
无向的，存储与查询统一按站点编号升序规范化。
"""

import math

LEVELS = ("light", "heavy", "severe")
LEVEL_LABELS = {"light": "轻度拥挤", "heavy": "重度拥挤", "severe": "严重拥挤"}


class CongestionError(ValueError):
    """等级非法、加价非法或边不存在等可预期的拒绝原因。"""


def validate_level(level: str) -> str:
    if not isinstance(level, str) or level not in LEVELS:
        raise CongestionError(f"非法拥挤等级: {level!r}，可选 {', '.join(LEVELS)}")
    return level


def validate_surcharge(amount) -> float:
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise CongestionError(f"非法加价: {amount!r}")
    value = float(amount)
    if not math.isfinite(value) or value < 0:
        raise CongestionError(f"加价必须为非负有限数值: {amount!r}")
    return round(value, 2)


def edge_key(a: str, b: str) -> tuple[str, str]:
    """无向边规范化：编号较小的站点在前。"""
    return tuple(sorted((a, b)))  # type: ignore[return-value]


def surcharge_along_path(
    path_edges: list[tuple[str, str]], congestion: dict[tuple[str, str], dict]
) -> tuple[list[dict], float]:
    """沿路径逐边累加拥挤加价。

    congestion 以规范化边为键，值为 {"level", "surcharge"}。
    返回途经的拥挤边明细（按途经顺序）与附加合计。
    """
    items: list[dict] = []
    total = 0.0
    for a, b in path_edges:
        info = congestion.get(edge_key(a, b))
        if not info:
            continue
        items.append(
            {"a": a, "b": b, "level": info["level"], "surcharge": round(float(info["surcharge"]), 2)}
        )
        total += float(info["surcharge"])
    return items, round(total, 2)
