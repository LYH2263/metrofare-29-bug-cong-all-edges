from fastapi import APIRouter
from app.services.metro_service import MetroService

router = APIRouter(tags=["settings"])

@router.get("/settings")
def get_settings():
    with MetroService() as s:
        return s.settings()
