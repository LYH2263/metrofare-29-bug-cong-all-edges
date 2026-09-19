from pydantic import BaseModel


class CongestionRequest(BaseModel):
    a: str
    b: str
    level: str
    surcharge: float
