from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import Base, engine
from models import Kund, Fordon, Anvandare
from auth import get_current_user, create_access_token, verify_password_argon2, verify_password_bcrypt, get_password_hash, auth_router
from datetime import date
from schemas.schemas import AnvandareRegistrering, FordonSkapa
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from database import SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✅ Route principale per la homepage
@app.get("/")
def home():
    return {"message": "API FastAPI live - Benvenuto!"}

# Middleware CORS per React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://fastapi-project-1-qd8d.onrender.com/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router autenticazione
app.include_router(auth_router)

# DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === AUTENTICAZIONE ===

@app.post("/register")
def register_anvandare(data: AnvandareRegistrering, db: Session = Depends(get_db)):
    if db.query(Anvandare).filter(Anvandare.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email redan registrerad")
    hashed_pw = get_password_hash(data.password)
    anvandare = Anvandare(email=data.email, hashed_password=hashed_pw)
    db.add(anvandare)
    db.commit()
    db.refresh(anvandare)
    return {"msg": "Användare skapad"}

@app.get("/me")
def get_me(current_anvandare: Anvandare = Depends(get_current_user)):
    return {"email": current_anvandare.email}

# === KUNDER ===

@app.post("/kunder/")
def skapa_kund(kund: dict, db: Session = Depends(get_db), current_anvandare: Anvandare = Depends(get_current_user)):
    ny_kund = Kund(**kund)
    db.add(ny_kund)
    db.commit()
    db.refresh(ny_kund)
    return ny_kund

@app.get("/kunder/")
def lista_kunder(db: Session = Depends(get_db), current_anvandare: Anvandare = Depends(get_current_user)):
    return db.query(Kund).all()

@app.get("/kunder/{kund_id}")
def hamta_kund(kund_id: int, db: Session = Depends(get_db), current_anvandare: Anvandare = Depends(get_current_user)):
    kund = db.query(Kund).filter(Kund.id == kund_id).first()
    if not kund:
        raise HTTPException(status_code=404, detail="Kund hittades inte")
    return kund

@app.delete("/kunder/{kund_id}")
def radera_kund(kund_id: int, db: Session = Depends(get_db), current_anvandare: Anvandare = Depends(get_current_user)):
    kund = db.query(Kund).filter(Kund.id == kund_id).first()
    if not kund:
        raise HTTPException(status_code=404, detail="Kund hittades inte")
    db.delete(kund)
    db.commit()
    return {"ok": True}

# === FORDON ===

@app.post("/veicoli")
def skapa_fordon_global(fordon: FordonSkapa, db: Session = Depends(get_db), current_anvandare: Anvandare = Depends(get_current_user)):
    kund = db.query(Kund).filter(Kund.id == fordon.kund_id).first()
    if not kund:
        raise HTTPException(status_code=404, detail="Kund hittades inte")

    nytt_fordon = Fordon(
        registreringsnummer=fordon.registreringsnummer,
        besiktningsdatum=fordon.besiktningsdatum,
        fordonstyp=fordon.fordonstyp,
        internnummer=fordon.internnummer,
        anteckningar=fordon.anteckningar,
        kund_id=fordon.kund_id,
    )
    db.add(nytt_fordon)
    db.commit()
    db.refresh(nytt_fordon)
    return nytt_fordon

@app.get("/kunder/{kund_id}/fordon/")
def lista_fordon(kund_id: int, db: Session = Depends(get_db), current_anvandare: Anvandare = Depends(get_current_user)):
    return db.query(Fordon).filter(Fordon.kund_id == kund_id).all()

@app.delete("/kunder/{kund_id}/fordon/{registreringsnummer}")
def radera_fordon(kund_id: int, registreringsnummer: str, db: Session = Depends(get_db), current_anvandare: Anvandare = Depends(get_current_user)):
    fordon = db.query(Fordon).filter(
        Fordon.kund_id == kund_id,
        Fordon.registreringsnummer == registreringsnummer
    ).first()
    if not fordon:
        raise HTTPException(status_code=404, detail="Fordon hittades inte")
    db.delete(fordon)
    db.commit()
    return {"ok": True}
