from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, database, crud

app = FastAPI(title="BookCircle API")

# Crear tablas en la base de datos
models.Base.metadata.create_all(bind=database.engine)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============= AUTH =============
@app.post("/auth/register", response_model=schemas.UserOut, status_code=201, tags=["Auth"])
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db=db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    db_username = crud.get_user_by_username(db=db, username=user_in.username)
    if db_username:
        raise HTTPException(status_code=400, detail="Username ya registrado")

    new_user = crud.create_user(db=db, user=user_in)
    return new_user

# ============= CLUBS =============
@app.get("/clubs", response_model=list[schemas.ClubOut], status_code=200, tags=["Clubs"])
def get_clubs(db: Session = Depends(get_db)):
    clubs = crud.get_clubs(db=db)
    return clubs

# ============= MEETINGS =============
@app.get("/clubs/{club_id}/meetings/{meeting_id}", response_model=schemas.MeetingDetail, tags=["Meetings"])
def get_meeting_details(club_id: int, meeting_id: int, db: Session = Depends(get_db)):
    db_meeting = crud.get_meeting(db, meeting_id=meeting_id)
    if db_meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    if db_meeting.club_id != club_id:
        raise HTTPException(status_code=404, detail="Meeting not found in this club")
    return db_meeting

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
