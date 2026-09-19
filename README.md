# 13-metrofare（地铁票价）

Metrofare — 站间最短站数 + 分段票价表

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4200 |
| API | http://localhost:9200 |

## 主链

选起终点站 → 按站数/里程规则算票价 → 出示票价卡

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
