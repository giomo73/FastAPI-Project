from pydantic import BaseModel
from typing import Optional, List

class KundBas(BaseModel):
    namn: str
    telefon: Optional[str] = None
    email: Optional[str] = None
    anteckningar: Optional[str] = None

class KundSkapa(KundBas):
    id: int  # inserito manualmente

class KundVisa(KundBas):
    id: int

    class Config:
        orm_mode = True

