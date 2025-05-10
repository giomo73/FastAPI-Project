from pydantic import BaseModel
from typing import Optional
from datetime import date

# Schema per registrazione utente
class AnvandareRegistrering(BaseModel):
    email: str
    password: str

# Schema per creazione veicolo
class FordonSkapa(BaseModel):
    registreringsnummer: str
    kund_id: int
    fordonstyp: str
    besiktningsdatum: Optional[date] = None
    internnummer: Optional[str] = None
    anteckningar: Optional[str] = None
