# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

# Función para buscar un usuario por su email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Función para buscar un usuario por su nombre de usuario (username)
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# Función para crear un nuevo usuario (HU-Register)
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=user.password,
        full_name=user.fullName
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user