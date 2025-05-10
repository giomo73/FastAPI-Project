from fastapi import Depends, HTTPException, status, APIRouter, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from itsdangerous import URLSafeTimedSerializer
from mailer import send_reset_email  # Aggiunto per invio email
from passlib.exc import UnknownHashError  # Importa correttamente l'eccezione
from models import Anvandare
from database import SessionLocal

# === Configurazione token ===
SECRET_KEY = "supersecretkey"  # Cambia in produzione
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
serializer = URLSafeTimedSerializer(SECRET_KEY)  # Per generare il link di reset password

# Definisci contesti separati per bcrypt e argon2
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter()

# === Gestione DB ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === Password ===
def verify_password_argon2(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False  # Indica che l'hash non è argon2

def verify_password_bcrypt(plain_password, hashed_password):
    try:
        return bcrypt_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False # Indica che l'hash non è bcrypt

def get_password_hash(password):
    # Crea un nuovo hash usando argon2
    return pwd_context.hash(password)

def update_password_if_needed(user: Anvandare, password: str, db: Session):
    # Se la password non è hashata con argon2, aggiornala
    if not pwd_context.identify(user.hashed_password):
        print("Password hash outdated, updating to argon2...")
        user.hashed_password = get_password_hash(password)
        db.commit()

# === JWT ===
def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# === Current User ===
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ogiltiga uppgifter",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(Anvandare).filter(Anvandare.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# === Registrazione utente con ruolo ===
@router.post("/register")
def register_anvandare(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")  # Assegna "user" come ruolo di default

    if db.query(Anvandare).filter(Anvandare.email == email).first():
        raise HTTPException(status_code=400, detail="Email redan registrerad")

    hashed_pw = get_password_hash(password)
    user = Anvandare(email=email, hashed_password=hashed_pw, role=role)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"msg": "Användare skapad", "email": user.email, "role": user.role}

# === Reset Password Request ===
@router.post("/reset-password-request")
async def reset_password_request(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    user = db.query(Anvandare).filter(Anvandare.email == email).first()
    if not user:
        return {"message": "Om e-posten finns, skickas en länk."}

    token = serializer.dumps(email, salt="reset-password")
    reset_link = f"http://localhost:5173/reset-password?token={token}"

    # Invia email reale
    await send_reset_email(email, reset_link)

    return {"message": "Länk skickad"}

# === Reset Password ===
@router.post("/reset-password")
def reset_password(data: dict = Body(...), db: Session = Depends(get_db)):
    token = data.get("token")
    new_password = data.get("new_password")

    try:
        email = serializer.loads(token, salt="reset-password", max_age=3600)
    except Exception:
        raise HTTPException(status_code=400, detail="Ogiltig eller utgången länk")

    user = db.query(Anvandare).filter(Anvandare.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Användare hittades inte")

    user.hashed_password = get_password_hash(new_password)
    db.commit()

    return {"message": "Lösenord uppdaterat"}