from pydantic import BaseModel
from typing import Optional
from datetime import date
from models.fordon import FordonTyp

class FordonBas(BaseModel):
    registreringsnummer: str
    besiktningsdatum: Optional[date] = None
    fordonstyp: FordonTyp

class FordonSkapa(FordonBas):
    pass

class FordonVisa(FordonBas):
    id: int
    kund_id: int

    class Config:
        orm_mode = True

