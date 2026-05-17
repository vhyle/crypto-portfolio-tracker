import bcrypt
from fastapi import APIRouter, HTTPException
from fastapi import Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserCreate, UserLogin, UserResponse, Token
from models import User
from security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user : UserCreate, db : Session = Depends(get_db)):
    # Handle the fact that username can already exist
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")
    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        password=hashed_password
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username already exists")
    return new_user

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if not existing_user or not verify_password(user.password, existing_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(existing_user.id)})
    return {"access_token": access_token}


