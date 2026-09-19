from fastapi import APIRouter
from app.services.metro_service import MetroService

router = APIRouter(tags=["fares"])

@router.get("/fare-rules")
def fare_rules():
    with MetroService() as s:
        return {"items": s.fare_rules()}
