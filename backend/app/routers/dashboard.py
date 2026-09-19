from fastapi import APIRouter
from app.services.metro_service import MetroService

router = APIRouter(tags=["dashboard"])

@router.get("/dashboard")
def dashboard():
    with MetroService() as s:
        return s.dashboard()
