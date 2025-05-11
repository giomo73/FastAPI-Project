from sqlalchemy.orm import Session
from database import SessionLocal
from hashing import get_password_hash
from models import Anvandare

db: Session = SessionLocal()

# Utenti da aggiornare
users = {
    "giovanni.morelli@ststrailerservice.se": "270973",
    "ulrik.hansen@ststrailerservice.se": "stsore2025",
}

for email, plain_pw in users.items():
    user = db.query(Anvandare).filter(Anvandare.email == email).first()
    if user:
        user.hashed_password = get_password_hash(plain_pw)
        db.commit()
        print(f"Aggiornata password hash per {email}")
    else:
        print(f"Utente {email} non trovato")
