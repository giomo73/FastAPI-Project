from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Modifica qui il percorso con il tuo percorso reale su OneDrive
ONEDRIVE_PATH = os.path.expanduser("C:/Users/Giovanni-STS/OneDrive/Dashboard/mydb.db")

# SQLite URL di connessione
DATABASE_URL = f"sqlite:///{ONEDRIVE_PATH}"

# Creazione del motore
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Sessione locale per accedere al database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base per i modelli ORM
Base = declarative_base()
