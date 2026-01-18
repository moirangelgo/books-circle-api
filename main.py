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
        raise HTTPException(status_code=400, detail="Usuario ya registrado")

    new_user = crud.create_user(db=db, user=user_in)
    return new_user