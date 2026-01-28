# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    # En una app real, aquí usaríamos una librería como passlib para encriptar
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=user.password, # Recuerda: ¡esto debe encriptarse luego!
        full_name=user.fullName
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_clubs(db: Session):
    # SELECT * FROM CLUBES
    return db.query(models.Club).all()


def get_meeting(db: Session, meeting_id: int):
    return db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
