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

# CLUBS
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

### Endpoints: B o o k s ###

@app.get("/clubs/{club_id}/books", response_model=list[schemas.BookOut], status_code=200)
def get_books_by_club_id(club_id: int, db: Session = Depends(get_db)):
    books = crud.get_books_by_club_id(db=db, club_id=club_id)
    if not books:
        raise HTTPException(status_code=404, detail="Libros no encontrados")
    return books


@app.post("/clubs/{club_id}/books", response_model=schemas.BookOut, status_code=201)
def create_book(club_id: int, book_in: schemas.BookCreate, db: Session = Depends(get_db)):
    new_book = crud.create_book(db=db, book=book_in)
    if not new_book:
        raise HTTPException(status_code=404, detail="Libro no creado")
    return new_book


@app.get("/clubs/{club_id}/books/{book_id}", response_model=schemas.BookOut, status_code=200)
def get_book_details(club_id: int, book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book_by_id(db=db, book_id=book_id, club_id=club_id)
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return book


@app.get("/clubs/{club_id}/books/{book_id}/votes", status_code=200)
def get_book_votes(club_id: int, book_id: int, db: Session = Depends(get_db)):
    return crud.add_votes_by_book_id(db=db, book_id=book_id, club_id=club_id)


@app.delete("/clubs/{club_id}/books/{book_id}/votes", status_code=204)
def delete_book_votes(club_id: int, book_id: int, db: Session = Depends(get_db)):
    return crud.delete_votes_by_book_id(db=db, book_id=book_id, club_id=club_id)    

#FUnciones faltantes GET progres y PUT update_progress
@app.get("/clubs/{clubId}/books/{bookId}/progress", status_code=200)
def get_reading_progress(clubId: int, bookId: int, db: Session = Depends(get_db)):
    progress = crud.get_book_progress(db=db, book_id=bookId, club_id=clubId)
    if progress is None:
        raise HTTPException(status_code=404, detail="Libro o progreso no encontrado")
    return {"progress": progress}

@app.put("/clubs/{clubId}/books/{bookId}/progress", response_model=schemas.BookOut, status_code=200)
def update_reading_progress(clubId: int, bookId: int, progress: int, db: Session = Depends(get_db)):
    updated_book = crud.update_book_progress(db=db, book_id=bookId, club_id=clubId, progress=progress)
    if not updated_book:
        raise HTTPException(status_code=404, detail="No se pudo actualizar el progreso: Libro no encontrado")
    return updated_book




# REVIEWS
@app.get("/clubs/{club_id}/books/{book_id}/reviews", response_model=list[schemas.ReviewOut], status_code=200)
def get_reviews_by_book_id(club_id: int, book_id: int, db: Session = Depends(get_db)):
    reviews = crud.get_reviews_by_book_id(db=db, book_id=book_id, club_id=club_id)
    if not reviews:
        raise HTTPException(status_code=404, detail="Reviews no encontrados")
    return reviews


@app.post("/clubs/{club_id}/books/{book_id}/reviews", response_model=schemas.ReviewOut, status_code=201)
def create_review(review_in: schemas.ReviewCreate, db: Session = Depends(get_db)):
    new_review = crud.create_review(db=db, review=review_in)
    if not new_review:
        raise HTTPException(status_code=404, detail="Review no creado")
    return new_review


@app.put("/clubs/{club_id}/books/{book_id}/reviews/{review_id}", response_model=schemas.ReviewOut, status_code=200)
def update_review(review_id: int, review_in: schemas.ReviewUpdate, db: Session = Depends(get_db)):
    updated_review = crud.update_review(db=db, review=review_in)
    if not updated_review:
        raise HTTPException(status_code=404, detail="Review no actualizado")
    return updated_review


@app.delete("/clubs/{club_id}/books/{book_id}/reviews/{review_id}", status_code=204)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    deleted_review = crud.delete_review(db=db, review_id=review_id)
    if not deleted_review:
        raise HTTPException(status_code=404, detail="Review no eliminado")
    return


# MEETINGS
@app.get("/clubs/{club_id}/meetings", status_code=200)
def meetings(club_id: int, db: Session = Depends(get_db)):
    return crud.get_meetings_by_club_id(db=db, club_id=club_id)


@app.get("/clubs/{club_id}/meetings/{meeting_id}", status_code=200)
def meetings(club_id: int, meeting_id:int, db: Session = Depends(get_db)):
    return crud.get_meetings_by_id(db=db, meeting_id=meeting_id)


@app.post("/clubs/{club_id}/meetings", status_code=201)
def meetings(meeting : schemas.MeetingCreate, db: Session = Depends(get_db)):
    meeting = crud.create_meeting(db=db, meeting=meeting)
    if not meeting:
        raise HTTPException(status_code=400, detail="No se pudo crear")
    return


# MEETINGS ATENDANCE
@app.put("/clubs/{club_id}/meetings/{meeting_id}/attendance",response_model=schemas.MeetingAttendanceOut)
def confirm_attendance(club_id: int, meeting_id: int, attendance_in: schemas.MeetingAttendanceCreate, db: Session = Depends(get_db)):
    return {
        "userId": "usr_abc123",
        "meetingId": f"mtg_{meeting_id}",
        "status": attendance_in.status,
        "note": attendance_in.note,
    }

