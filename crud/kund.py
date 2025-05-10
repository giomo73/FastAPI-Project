from sqlalchemy.orm import Session
import models.kund as models
import schemas.kund as schemas

def skapa_kund(db: Session, kund: schemas.KundSkapa):
    ny_kund = models.Kund(
        id=kund.id,
        namn=kund.namn,
        telefon=kund.telefon,
        email=kund.email,
        anteckningar=kund.anteckningar
    )
    db.add(ny_kund)
    db.commit()
    db.refresh(ny_kund)
    return ny_kund

def hämta_kunder(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Kund).offset(skip).limit(limit).all()

def hämta_kund_med_id(db: Session, kund_id: int):
    return db.query(models.Kund).filter(models.Kund.id == kund_id).first()

