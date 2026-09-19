from fastapi import APIRouter
from app.services.metro_service import MetroService

router = APIRouter(tags=["edges"])

@router.get("/edges")
def list_edges():
    with MetroService() as s:
        return {"items": s.edges()}
