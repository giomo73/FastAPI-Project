from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

# Modello per i clienti (Kund)
class Kund(Base):
    __tablename__ = "kunder"  # Convenzione: nomi delle tabelle in minuscolo

    id = Column(Integer, primary_key=True, index=True)
    namn = Column(String)
    telefon = Column(String)
    email = Column(String)
    anteckningar = Column(String)

    # Relazione con il modello Fordon
    fordon = relationship("Fordon", back_populates="kund", cascade="all, delete")


# Modello per i veicoli (Fordon)
class Fordon(Base):
    __tablename__ = "fordon"

    id = Column(Integer, primary_key=True, index=True)
    registreringsnummer = Column(String(20), nullable=False, index=True)
    besiktningsdatum = Column(Date, nullable=True)  # ora facoltativo
    fordonstyp = Column(String(30), nullable=False)
    kund_id = Column(Integer, ForeignKey("kunder.id"), nullable=False)

    internnummer = Column(String(30), nullable=True)  # nuovo campo opzionale
    anteckningar = Column(Text, nullable=True)        # nuovo campo opzionale

    kund = relationship("Kund", back_populates="fordon")


# Modello per gli utenti (Anvandare)
class Anvandare(Base):
    __tablename__ = "anvandare"  # Convenzione in minuscolo

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # Memorizzato come hash
    role = Column(String, default="admin")  # Campo 'role' opzionale
