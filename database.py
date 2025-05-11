from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Percorso compatibile con ambienti come Render
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://verkstad_db_user:2d3z9ykneIOHmIHK0SeFp6fYYwGeBxvz@dpg-d0g6d4adbo4c73b2hnig-a.frankfurt-postgres.render.com/verkstad_db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
