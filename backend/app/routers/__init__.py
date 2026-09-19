from fastapi import APIRouter

from app.routers import (
    congestion,
    dashboard,
    edges,
    fares,
    history,
    quote,
    settings,
    stations,
)

api = APIRouter(prefix="/api")
for r in (dashboard, stations, edges, fares, quote, history, settings, congestion):
    api.include_router(r.router)
