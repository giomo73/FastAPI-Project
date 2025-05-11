from fastapi import Depends, HTTPException, status, APIRouter, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from mailer import send_reset_email
from models import Anvandare
from database import get_db
from hashing import get_password_hash

# === Configurazione token ===
SECRET_KEY = "supersecretkey"  # Cambia in produzione
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
serializer = URLSafeTimedSerializer(SECRET_KEY)

# === Password contexts ===
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
argon2_context = CryptContext(schemes=["argon2"], deprecated="auto")

# === OAuth2 ===
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
auth_router = APIRouter()

# === Utility Password ===
def verify_password_argon2(plain_password, hashed_password):
    try:
        return argon2_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False

def verify_password_bcrypt(plain_password, hashed_password):
    try:
        return bcrypt_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False

def update_password_if_needed(user: Anvandare, password: str, db: Session):
    if not argon2_context.identify(user.hashed_password):
        print("Password hash outdated, updating to argon2...")
        user.hashed_password = get_password_hash(password)
        db.commit()

# === JWT Token generation ===
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# === Current user extraction ===
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ogiltiga uppgifter",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Anvandare).filter(Anvandare.email == email).first()
    if not user:
        raise credentials_exception
    return user

# === ROUTES ===

# 🔐 REGISTRAZIONE
@auth_router.post("/register")
def register_anvandare(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if db.query(Anvandare).filter(Anvandare.email == email).first():
        raise HTTPException(status_code=400, detail="Email redan registrerad")

    hashed_pw = get_password_hash(password)
    user = Anvandare(email=email, hashed_password=hashed_pw, role=role)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"msg": "Användare skapad", "email": user.email, "role": user.role}

# 🔐 LOGIN
@auth_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print("==> Richiesta ricevuta su /login")
    email = form_data.username
    password = form_data.password

    user = db.query(Anvandare).filter(Anvandare.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Felaktiga inloggningsuppgifter")

    if verify_password_argon2(password, user.hashed_password):
        pass
    elif verify_password_bcrypt(password, user.hashed_password):
        update_password_if_needed(user, password, db)
    else:
        raise HTTPException(status_code=401, detail="Felaktiga inloggningsuppgifter")

    token = create_access_token({"sub": user.email})
    print("==> Login OK")
    return {"access_token": token, "token_type": "bearer"}

# 🔐 RESET PASSWORD - richiesta
@auth_router.post("/reset-password-request")
async def reset_password_request(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    user = db.query(Anvandare).filter(Anvandare.email == email).first()
    if not user:
        return {"message": "Om e-posten finns, skickas en länk."}

    token = serializer.dumps(email, salt="reset-password")
    reset_link = f"http://localhost:5173/reset-password?token={token}"
    await send_reset_email(email, reset_link)

    return {"message": "Länk skickad"}

# 🔐 RESET PASSWORD - conferma
@auth_router.post("/reset-password")
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

# 🐞 DEBUG - Vedi utenti registrati
@auth_router.get("/debug/users", tags=["Debug"])
def debug_get_users(db: Session = Depends(get_db)):
    users = db.query(Anvandare).all()
    return [{"id": u.id, "email": u.email, "role": u.role} for u in users]
