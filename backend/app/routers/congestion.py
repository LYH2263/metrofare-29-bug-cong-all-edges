from fastapi import APIRouter, HTTPException

from app.modules.congestion_surcharge import LEVELS, CongestionError
from app.schemas.congestion import CongestionRequest
from app.services.metro_service import MetroService

router = APIRouter(tags=["congestion"])


@router.get("/congestion")
def list_congestion():
    with MetroService() as s:
        return {"items": s.congestion_edges(), "levels": list(LEVELS)}


@router.put("/congestion")
def set_congestion(body: CongestionRequest):
    with MetroService() as s:
        try:
            return s.set_congestion(body.a, body.b, body.level, body.surcharge)
        except CongestionError as e:
            raise HTTPException(status_code=400, detail=str(e))


@router.delete("/congestion")
def clear_congestion(a: str, b: str):
    with MetroService() as s:
        try:
            return s.clear_congestion(a, b)
        except CongestionError as e:
            raise HTTPException(status_code=400, detail=str(e))
