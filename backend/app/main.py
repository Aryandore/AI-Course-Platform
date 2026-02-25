from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import engine, get_db
from passlib.context import CryptContext

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    print("Password length:", len(user.password))

    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hashed_pw,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user