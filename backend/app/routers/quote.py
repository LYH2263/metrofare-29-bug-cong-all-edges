from fastapi import APIRouter
from app.schemas.quote import QuoteRequest
from app.services.metro_service import MetroService

router = APIRouter(tags=["quote"])

@router.post("/quote")
def post_quote(body: QuoteRequest):
    with MetroService() as s:
        return s.quote(body.start, body.end, body.persist)
