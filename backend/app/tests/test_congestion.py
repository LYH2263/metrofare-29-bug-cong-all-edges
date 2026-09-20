import json

import pytest
from fastapi.testclient import TestClient

from app import seed
from app.engines.route_quote import quote_route
from app.engines.graph_bfs import shortest_path
from app.main import app
from app.modules.congestion_surcharge import (
    CongestionError,
    edge_key,
    surcharge_along_path,
    validate_level,
    validate_surcharge,
)
from app.services.metro_service import MetroService

EDGES = [("A1", "A2"), ("A2", "A3"), ("A2", "B1"), ("B1", "B2")]
RULES = [
    {"max_hops": 2, "price": 3.0},
    {"max_hops": 4, "price": 4.0},
    {"max_hops": None, "price": 6.0},
]


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "test.db")
    seed.init_db()
    with TestClient(app) as c:
        yield c


# ---------- 纯函数 ----------

def test_shortest_path_returns_ordered_edges():
    assert shortest_path(EDGES, "A1", "A3") == [("A1", "A2"), ("A2", "A3")]
    assert shortest_path(EDGES, "A1", "B2") == [("A1", "A2"), ("A2", "B1"), ("B1", "B2")]
    assert shortest_path(EDGES, "A1", "A1") == []
    assert shortest_path(EDGES, "A1", "ZZ") is None


def test_edge_key_is_undirected():
    assert edge_key("B1", "A2") == ("A2", "B1")


def test_validate_level():
    assert validate_level("heavy") == "heavy"
    with pytest.raises(CongestionError):
        validate_level("explosive")


def test_validate_surcharge():
    assert validate_surcharge(2) == 2.0
    assert validate_surcharge(0) == 0.0
    for bad in (-0.01, float("inf"), float("nan"), "1元", None, True):
        with pytest.raises(CongestionError):
            validate_surcharge(bad)


def test_surcharge_along_path_sums_in_order():
    congestion = {
        ("A1", "A2"): {"level": "light", "surcharge": 0.5},
        ("A2", "B1"): {"level": "heavy", "surcharge": 1.5},
    }
    items, total = surcharge_along_path(
        [("A1", "A2"), ("A2", "B1"), ("B1", "B2")], congestion
    )
    assert total == 2.0
    assert [(i["a"], i["b"]) for i in items] == [("A1", "A2"), ("A2", "B1")]
    assert items[1]["level"] == "heavy"


# ---------- 询价引擎 ----------

def test_quote_without_congestion_has_zero_surcharge():
    q = quote_route(EDGES, "A1", "B2", RULES)
    assert q["reachable"]
    assert q["hops"] == 3
    assert q["base_fare"] == 4.0
    assert q["congestion_total"] == 0.0
    assert q["congestion_edges"] == []
    assert q["payable"] == 4.0
    assert q["fare"] == q["payable"]


def test_quote_sums_congestion_on_shortest_path():
    congestion = {edge_key("B1", "A2"): {"level": "heavy", "surcharge": 1.5}}
    q = quote_route(EDGES, "A1", "B2", RULES, congestion)
    assert q["base_fare"] == 4.0
    assert q["congestion_total"] == 1.5
    assert q["payable"] == 5.5
    assert q["congestion_edges"] == [
        {"a": "A2", "b": "B1", "level": "heavy", "surcharge": 1.5}
    ]


def test_quote_unreachable_shape():
    q = quote_route(EDGES, "A1", "ZZ", RULES)
    assert q["reachable"] is False
    assert q["payable"] is None
    assert q["congestion_total"] == 0.0


# ---------- 服务层：落库与拒绝 ----------

def test_set_clear_list_congestion(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "test.db")
    seed.init_db()
    with MetroService() as s:
        assert s.congestion_edges() == []
        saved = s.set_congestion("B1", "A2", "heavy", 1.5)  # 反向传入也规范化
        assert saved == {"a": "A2", "b": "B1", "level": "heavy", "surcharge": 1.5}
        assert s.congestion_edges() == [saved]

        # 重复设置即覆盖
        s.set_congestion("A2", "B1", "severe", 3.0)
        assert s.congestion_edges() == [
            {"a": "A2", "b": "B1", "level": "severe", "surcharge": 3.0}
        ]

        cleared = s.clear_congestion("A2", "B1")
        assert cleared["removed"] == 1
        assert s.congestion_edges() == []


def test_set_rejects_bad_level_and_missing_edge(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "test.db")
    seed.init_db()
    with MetroService() as s:
        with pytest.raises(CongestionError):
            s.set_congestion("A2", "B1", "explosive", 1.0)
        with pytest.raises(CongestionError):
            s.set_congestion("A1", "B2", "light", 1.0)  # 不存在的邻接边
        with pytest.raises(CongestionError):
            s.set_congestion("A2", "B1", "light", -0.5)
        assert s.congestion_edges() == []


def test_readonly_quote_does_not_persist(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "test.db")
    seed.init_db()
    with MetroService() as s:
        before = len(s.history())
        out = s.quote("A1", "B2", persist=False)
        assert out["run_id"] is None
        assert len(s.history()) == before  # 只读询价不写记录
        out = s.quote("A1", "B2", persist=True)
        assert out["run_id"] is not None
        assert len(s.history()) == before + 1


def test_history_snapshot_keeps_congestion_after_clearing(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "test.db")
    seed.init_db()
    with MetroService() as s:
        s.set_congestion("A2", "B1", "heavy", 1.5)
        old = s.quote("A1", "B2", persist=True)
        run_id = old["run_id"]
        assert [e["b"] for e in old["congestion_edges"]] == ["B1"]

        s.clear_congestion("A2", "B1")  # 市心—北苑
        fresh = s.quote("A1", "B2", persist=False)
        assert fresh["congestion_edges"] == []
        assert fresh["payable"] == 4.0

        record = s.run(run_id)
        snapshot = json.loads(record["result_json"])
        assert snapshot["congestion_edges"] == [
            {"a": "A2", "b": "B1", "level": "heavy", "surcharge": 1.5}
        ]
        assert snapshot["congestion_total"] == 1.5
        assert snapshot["payable"] == 5.5

        # 再次清边必须是幂等的，且依旧不改写旧记录
        s.clear_congestion("A2", "B1")
        again = json.loads(s.run(run_id)["result_json"])
        assert again["congestion_edges"][0]["b"] == "B1"
        assert again["congestion_total"] == 1.5


def test_history_snapshot_only_lists_congestion_on_path(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "test.db")
    seed.init_db()
    with MetroService() as s:
        # 途经边 A1—A2 加价 0.5；B1—B2 当时也是拥挤边，但不在 A1→A3 的途经上
        s.set_congestion("A1", "A2", "light", 0.5)
        s.set_congestion("B1", "B2", "severe", 9.0)
        out = s.quote("A1", "A3", persist=True)
        assert out["congestion_total"] == 0.5
        assert out["congestion_edges"] == [
            {"a": "A1", "b": "A2", "level": "light", "surcharge": 0.5}
        ]

        snapshot = json.loads(s.run(out["run_id"])["result_json"])
        # 详情列表只含写入当时途经上的边，合计与列表一致
        assert snapshot["congestion_edges"] == [
            {"a": "A1", "b": "A2", "level": "light", "surcharge": 0.5}
        ]
        assert snapshot["congestion_total"] == sum(
            e["surcharge"] for e in snapshot["congestion_edges"]
        )

        # 清掉非途经边后，旧记录同样不受影响
        s.clear_congestion("B1", "B2")
        snapshot2 = json.loads(s.run(out["run_id"])["result_json"])
        assert snapshot2 == snapshot


# ---------- HTTP 接口 ----------

def test_api_congestion_crud_and_rejections(client):
    r = client.put(
        "/api/congestion", json={"a": "A2", "b": "B1", "level": "heavy", "surcharge": 1.5}
    )
    assert r.status_code == 200
    assert r.json()["a"] == "A2"

    bad_level = client.put(
        "/api/congestion", json={"a": "A1", "b": "A2", "level": "nope", "surcharge": 1}
    )
    assert bad_level.status_code == 400

    missing_edge = client.put(
        "/api/congestion", json={"a": "A1", "b": "B2", "level": "light", "surcharge": 1}
    )
    assert missing_edge.status_code == 400

    listed = client.get("/api/congestion").json()["items"]
    assert [(e["a"], e["b"]) for e in listed] == [("A2", "B1")]

    deleted = client.delete("/api/congestion", params={"a": "A2", "b": "B1"})
    assert deleted.status_code == 200
    assert client.get("/api/congestion").json()["items"] == []


def test_api_quote_breakdown(client):
    client.put(
        "/api/congestion", json={"a": "A2", "b": "B1", "level": "heavy", "surcharge": 1.5}
    )
    r = client.post("/api/quote", json={"start": "A1", "end": "B2", "persist": False})
    body = r.json()
    assert body["base_fare"] == 4.0
    assert body["congestion_total"] == 1.5
    assert body["payable"] == 5.5
    assert body["congestion_edges"][0]["b"] == "B1"

    client.delete("/api/congestion", params={"a": "B1", "b": "A2"})
    after = client.post(
        "/api/quote", json={"start": "A1", "end": "B2", "persist": False}
    ).json()
    assert after["congestion_edges"] == []
    assert after["payable"] == 4.0


def test_api_history_detail_and_404(client):
    run_id = client.post(
        "/api/quote", json={"start": "A1", "end": "A3", "persist": True}
    ).json()["run_id"]
    detail = client.get(f"/api/history/{run_id}")
    assert detail.status_code == 200
    snapshot = json.loads(detail.json()["result_json"])
    assert snapshot["start"] == "A1"
    assert client.get("/api/history/9999").status_code == 404


def test_api_edges_embed_congestion(client):
    client.put(
        "/api/congestion", json={"a": "A1", "b": "A2", "level": "light", "surcharge": 0.5}
    )
    edges = client.get("/api/edges").json()["items"]
    flagged = {e["b"] if e["a"] == "A1" else e["a"]: e for e in edges if e["level"]}
    row = flagged["A2"]
    assert row["level"] == "light" and row["surcharge"] == 0.5
