from sqlalchemy.orm import Session
import models.fordon as models
import schemas.fordon as schemas

def lägg_till_fordon(db: Session, kund_id: int, fordon: schemas.FordonSkapa):
    nytt_fordon = models.Fordon(
        registreringsnummer=fordon.registreringsnummer,
        besiktningsdatum=fordon.besiktningsdatum,
        fordonstyp=fordon.fordonstyp,
        kund_id=kund_id
    )
    db.add(nytt_fordon)
    db.commit()
    db.refresh(nytt_fordon)
    return nytt_fordon

def hämta_fordon_för_kund(db: Session, kund_id: int):
    return db.query(models.Fordon).filter(models.Fordon.kund_id == kund_id).all()
