from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import engine, get_db
from passlib.context import CryptContext
from app.auth import verify_password, create_access_token
from app.auth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm


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



@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }



@app.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/courses", response_model=schemas.CourseResponse)
def create_course(
    course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    # Only instructors can create courses
    if current_user.role != "instructor":
        raise HTTPException(status_code=403, detail="Only instructors can create courses")

    new_course = models.Course(
        title=course.title,
        description=course.description,
        price=course.price,
        instructor_id=current_user.id
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course

@app.get("/courses", response_model=list[schemas.CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(models.Course).all()
    return courses