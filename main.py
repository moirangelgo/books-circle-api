from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, crud

app = FastAPI(title="BookCircle API")

models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/auth/register", response_model=schemas.UserOut, status_code=201)
def register_user(
                    user_in: schemas.UserCreate, 
                    db: Session = Depends(get_db)
                ):
    
    db_user = crud.get_user_by_email(db=db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    db_username = crud.get_user_by_username(db=db, username=user_in.username)
    if db_username:
        raise HTTPException(status_code=400, detail="Username ya registrado")

    new_user = crud.create_user(db=db, user=user_in)
    return new_user


@app.get("/clubs", response_model=list[schemas.ClubOut], status_code=200)
def clubs(db: Session = Depends(get_db)):
    clubs = crud.get_clubs(db=db)
    return clubs


@app.post("/clubs", response_model=schemas.ClubOut, status_code=201)
def create_club(club_in: schemas.ClubCreate, db: Session = Depends(get_db)):
    new_club = crud.create_club(db=db, club=club_in)
    return new_club


@app.put("/clubs/{club_id}", response_model=schemas.ClubOut, status_code=200)
def update_club(club_id: int, club_in: schemas.ClubCreate, db: Session = Depends(get_db)):
    new_club = crud.update_club(db=db, club=club_in, club_id=club_id)
    if not new_club:
        raise HTTPException(status_code=404, detail="Club no encontrado")
    return new_club


@app.get("/clubs/{club_id}", response_model=schemas.ClubOut, status_code=200)
def get_club(club_id: int, db: Session = Depends(get_db)):
    club = crud.get_club_by_id(db=db, club_id=club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club no encontrado")
    return club


@app.delete("/clubs/{club_id}", status_code=204)
def delete_club(club_id: int, db: Session = Depends(get_db)):
    club = crud.delete_club(db=db, club_id=club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club no encontrado")
    return