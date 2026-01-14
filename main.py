from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API de Clubes de Lectura",
    description="API REST para gestionar clubes de lectura",
    version="1.0.0"
)

# ============= MODELOS (Schemas) =============

class Club(BaseModel):
    """Model representing a reading club"""
    id: int
    name: str
    description: str
    created_date: str
    favorite_genre: str
    members: int

class ClubCreate(BaseModel):
    """Model for creating a new club (without ID)"""
    name: str
    description: str
    favorite_genre: str
    members: int = 0

class ClubUpdate(BaseModel):
    """Model for updating a club (all fields optional)"""
    name: str | None = None
    description: str | None = None
    favorite_genre: str | None = None
    members: int | None = None

 #     ===     Books (Schemas)     ===    #
class Book(BaseModel):
    id: int
    club_id: int
    title: str
    author: str
    votes: int = 0
    progress: int = 0  # Porcentaje

class BookCreate(BaseModel):
    title: str
    author: str

class ProgressUpdate(BaseModel):
    progress: int


# ============= DATOS ESTÁTICOS (Simulación de BD) =============

clubs_db = {
    1: {
        "id": 1,
        "name": "Lectores Nocturnos",
        "description": "Club para amantes de la lectura nocturna",
        "created_date": "2024-01-15",
        "favorite_genre": "Misterio",
        "members": 25
    },
    2: {
        "id": 2,
        "name": "Fantasía y Más",
        "description": "Dedicado a la literatura fantástica",
        "created_date": "2024-02-20",
        "favorite_genre": "Fantasía",
        "members": 40
    },
    3: {
        "id": 3,
        "name": "Clásicos Eternos",
        "description": "Explorando la literatura clásica",
        "created_date": "2024-03-10",
        "favorite_genre": "Clásicos",
        "members": 15
    }
}
#Books (DB)
books_db = {
    1: {
        "id": 1, 
        "club_id": 1, 
        "title": "Cien años de soledad", 
        "author": "Gabo", 
        "votes": 5, 
        "progress": 20
        },
    2: {
        "id": 2, 
        "club_id": 1, 
        "title": "Drácula", 
        "author": "Bram Stoker", 
        "votes": 2, 
        "progress": 0
        }
}

# Variable para generar IDs únicos
next_id = 4

next_book_id = 3

# ============= ENDPOINTS =============

@app.get("/")
def root():
    """Endpoint raíz - Bienvenida"""
    return {
        "mensaje": "Bienvenido a la API de Clubes de Lectura",
        "documentacion": "/docs"
    }


@app.get("/clubs", response_model=list[Club], tags=["Clubs"])
def get_clubs():
    """
    Obtener todos los clubes de lectura
    
    Retorna una lista con todos los clubes registrados.
    """
    return list(clubs_db.values())


@app.post("/clubs", tags=["Clubs"])
def create_clubs(club: ClubCreate):
    return club


@app.get("/clubs/{clubId}", tags=["Clubs"])
def get_clubs(clubId: int) -> Club:
    return Club()


@app.put("/clubs/{clubId}", tags=["Clubs"])
def get_clubs(clubId: int) -> Club:
    return Club()


@app.delete("/clubs/{clubId}", tags=["Clubs"])
def get_clubs(clubId: int) -> int:
    return 204

#     ===           Books (ENDPOINTS)       ===       #


@app.get("/clubs/{clubId}/books", tags=["Books"])
def get_all_books_of_club(clubId: int):
    # Filtro librosue con el clubId
    resultado = []
    for book in books_db.values():
        if book["club_id"] == clubId:
            resultado.append(book)
    return resultado

@app.post("/clubs/{clubId}/books", tags=["Books"])
def create_book(clubId: int, book: BookCreate):
    global next_book_id
    # Diccionario del nuevo libro
    nuevo_libro = {
        "id": next_book_id,
        "club_id": clubId,
        "title": book.title,
        "author": book.author,
        "votes": 0,
        "progress": 0
    }
    books_db[next_book_id] = nuevo_libro
    next_book_id += 1
    return nuevo_libro

@app.get("/clubs/{clubId}/books/{bookId}", tags=["Books"])
def get_one_book(clubId: int, bookId: int):
    libro = books_db.get(bookId)
    if libro and libro["club_id"] == clubId:
        return libro
    raise HTTPException(status_code=404, detail="Libro no encontrado")

@app.post("/clubs/{clubId}/books/{bookId}/votes", tags=["Books"])
def add_vote(clubId: int, bookId: int):
    libro = books_db.get(bookId)
    if libro and libro["club_id"] == clubId:
        libro["votes"] += 1
        return {"mensaje": "Voto sumado", "total": libro["votes"]}
    raise HTTPException(status_code=404, detail="Libro no encontrado")

@app.delete("/clubs/{clubId}/books/{bookId}/votes", tags=["Books"])
def remove_vote(clubId: int, bookId: int):
    libro = books_db.get(bookId)
    if libro and libro["club_id"] == clubId:
        if libro["votes"] > 0:
            libro["votes"] -= 1
        return {"mensaje": "Voto restado", "total": libro["votes"]}
    raise HTTPException(status_code=404, detail="Libro no encontrado")

@app.get("/clubs/{clubId}/books/{bookId}/progress", tags=["Books"])
def get_progress(clubId: int, bookId: int):
    libro = books_db.get(bookId)
    if libro and libro["club_id"] == clubId:
        return {"progreso": libro["progress"]}
    raise HTTPException(status_code=404, detail="Libro no encontrado")

@app.put("/clubs/{clubId}/books/{bookId}/progress", tags=["Books"])
def update_progress(clubId: int, bookId: int, body: ProgressUpdate):
    libro = books_db.get(bookId)
    if libro and libro["club_id"] == clubId:
        libro["progress"] = body.progress
        return {"mensaje": "Progreso actualizado", "nuevo_progreso": libro["progress"]}
    raise HTTPException(status_code=404, detail="Libro no encontrado")
#       ===       Books (ENDPOINTS) FIN        ===       #

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
