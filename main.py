from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas, database, crud
from app.core import security
from jose import JWTError, jwt
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(title="BookCircle API", lifespan=lifespan)

# models.Base.metadata.create_all(bind=database.engine) # Removed in favor of lifespan

async def get_db():
    async with database.SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/register", response_model=schemas.UserOut, status_code=201)
async def register_user(
                    user_in: schemas.UserCreate, 
                    db: AsyncSession = Depends(get_db)
                ):
    
    db_user = await crud.get_user_by_email(db=db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    db_username = await crud.get_user_by_username(db=db, username=user_in.username)
    if db_username:
        raise HTTPException(status_code=400, detail="Username ya registrado")

    new_user = await crud.create_user(db=db, user=user_in)
    return new_user

# CLUBS
@app.get("/clubs", response_model=list[schemas.ClubOut], status_code=200)
async def clubs(db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    clubs = await crud.get_clubs(db=db)
    return clubs


@app.post("/clubs", response_model=schemas.ClubOut, status_code=201)
async def create_club(club_in: schemas.ClubCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_club = await crud.create_club(db=db, club=club_in)
    return new_club


@app.put("/clubs/{club_id}", response_model=schemas.ClubOut, status_code=200)
async def update_club(club_id: int, club_in: schemas.ClubCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_club = await crud.update_club(db=db, club=club_in, club_id=club_id)
    if not new_club:
        raise HTTPException(status_code=404, detail="Club no encontrado")
    return new_club


@app.get("/clubs/{club_id}", response_model=schemas.ClubOut, status_code=200)
async def get_club(club_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    club = await crud.get_club_by_id(db=db, club_id=club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club no encontrado")
    return club


@app.delete("/clubs/{club_id}", status_code=204)
async def delete_club(club_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    club = await crud.delete_club(db=db, club_id=club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club no encontrado")
    return

### Endpoints: B o o k s ###

@app.get("/clubs/{club_id}/books", response_model=list[schemas.BookOut], status_code=200)
async def get_books_by_club_id(club_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    books = await crud.get_books_by_club_id(db=db, club_id=club_id)
    if not books:
        raise HTTPException(status_code=404, detail="Libros no encontrados")
    return books


@app.post("/clubs/{club_id}/books", response_model=schemas.BookOut, status_code=201)
async def create_book(club_id: int, book_in: schemas.BookCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_book = await crud.create_book(db=db, book=book_in)
    if not new_book:
        raise HTTPException(status_code=404, detail="Libro no creado")
    return new_book


@app.get("/clubs/{club_id}/books/{book_id}", response_model=schemas.BookOut, status_code=200)
async def get_book_details(club_id: int, book_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    book = await crud.get_book_by_id(db=db, book_id=book_id, club_id=club_id)
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return book


@app.get("/clubs/{club_id}/books/{book_id}/votes", status_code=200)
async def get_book_votes(club_id: int, book_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return await crud.add_votes_by_book_id(db=db, book_id=book_id, club_id=club_id)


@app.delete("/clubs/{club_id}/books/{book_id}/votes", status_code=204)
async def delete_book_votes(club_id: int, book_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return await crud.delete_votes_by_book_id(db=db, book_id=book_id, club_id=club_id)    

#FUnciones faltantes GET progres y PUT update_progress
@app.get("/clubs/{clubId}/books/{bookId}/progress", status_code=200)
async def get_reading_progress(clubId: int, bookId: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    progress = await crud.get_book_progress(db=db, book_id=bookId, club_id=clubId)
    if progress is None:
        raise HTTPException(status_code=404, detail="Libro o progreso no encontrado")
    return {"progress": progress}

@app.put("/clubs/{clubId}/books/{bookId}/progress", response_model=schemas.BookOut, status_code=200)
async def update_reading_progress(clubId: int, bookId: int, progress: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    updated_book = await crud.update_book_progress(db=db, book_id=bookId, club_id=clubId, progress=progress)
    if not updated_book:
        raise HTTPException(status_code=404, detail="No se pudo actualizar el progreso: Libro no encontrado")
    return updated_book




# REVIEWS
@app.get("/clubs/{club_id}/books/{book_id}/reviews", response_model=list[schemas.ReviewOut], status_code=200)
async def get_reviews_by_book_id(club_id: int, book_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    reviews = await crud.get_reviews_by_book_id(db=db, book_id=book_id, club_id=club_id)
    if not reviews:
        raise HTTPException(status_code=404, detail="Reviews no encontrados")
    return reviews


@app.post("/clubs/{club_id}/books/{book_id}/reviews", response_model=schemas.ReviewOut, status_code=201)
async def create_review(review_in: schemas.ReviewCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_review = await crud.create_review(db=db, review=review_in)
    if not new_review:
        raise HTTPException(status_code=404, detail="Review no creado")
    return new_review


@app.put("/clubs/{club_id}/books/{book_id}/reviews/{review_id}", response_model=schemas.ReviewOut, status_code=200)
async def update_review(review_id: int, review_in: schemas.ReviewUpdate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    updated_review = await crud.update_review(db=db, review=review_in)
    if not updated_review:
        raise HTTPException(status_code=404, detail="Review no actualizado")
    return updated_review


@app.delete("/clubs/{club_id}/books/{book_id}/reviews/{review_id}", status_code=204)
async def delete_review(review_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    deleted_review = await crud.delete_review(db=db, review_id=review_id)
    if not deleted_review:
        raise HTTPException(status_code=404, detail="Review no eliminado")
    return


# MEETINGS
@app.get("/clubs/{club_id}/meetings", status_code=200)
async def meetings(club_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return await crud.get_meetings_by_club_id(db=db, club_id=club_id)


@app.get("/clubs/{club_id}/meetings/{meeting_id}", status_code=200)
async def meetings(club_id: int, meeting_id:int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return await crud.get_meetings_by_id(db=db, meeting_id=meeting_id)


@app.post("/clubs/{club_id}/meetings", status_code=201)
async def meetings(meeting : schemas.MeetingCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    meeting = await crud.create_meeting(db=db, meeting=meeting)
    if not meeting:
        raise HTTPException(status_code=400, detail="No se pudo crear")
    return

# = = = = = DELETE
@app.delete("/clubs/{club_id}/meetings/{meeting_id}", status_code=204)
async def cancel_meeting(club_id: int, meeting_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    deleted_meeting = await crud.delete_meeting(db=db, club_id=club_id, meeting_id=meeting_id)
    
    if not deleted_meeting:
        raise HTTPException(status_code=404, 
            detail="La reunión no existe o no pertenece a este club"
        )
    return #204 estado indica proceso exitoso pero no hay contenido de vuelta 

# MEETINGS ATENDANCE
@app.post("/clubs/{club_id}/meetings/{meeting_id}/attendance", status_code=201)
async def confirm_attendance(club_id: int, meeting_id: int, attendance_in: schemas.MeetingAttendanceCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    attendance = await crud.create_attendance_meeting(db, meeting_id, attendance_in)    
    if not attendance:
        raise HTTPException(status_code=400, detail="No se pudo crear")
    return
