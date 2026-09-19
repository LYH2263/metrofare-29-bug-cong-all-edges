from fastapi import APIRouter, HTTPException
from app.services.metro_service import MetroService

router = APIRouter(tags=["stations"])

@router.get("/stations")
def list_stations():
    with MetroService() as s:
        return {"items": s.stations()}

@router.get("/stations/{code}")
def get_station(code: str):
    with MetroService() as s:
        row = s.station(code)
        if not row:
            raise HTTPException(404)
        return row
