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

# Modelos para REVIEWS - - - 
class Review(BaseModel):
    '''Modelo que representa una reseña'''
    id: int 
    book_id: int
    user_id: int
    rating: int
    comment: str

class ReviewCreate(BaseModel):
    '''Modelo para crear una reseña'''
    book_id: int
    user_id: int
    rating: int
    comment: str

class ReviewUpdate(BaseModel):
    '''Modelo para actualizar una reseña '''
    rating: int | None = None
    comment: str | None = None


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

# Variable para generar IDs únicos
next_id = 4


# Datos para Reviews - - - - - 
reviews_db = {
    1: {
        "id": 1,
        "book_id": 101,
        "user_id": 1,
        "rating": 5,
        "comment": "¡Un libro que atrapa de inicio a fin!",
        "date": "2024-03-20"
    }
}
next_review_id = 2


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

# Endpoints REVIEWS - - - - - 
@app.get("/reviews", response_model=list[Review], tags=["Reviews"])
def get_reviews():
    """Listar todas las reseñas"""
    return list(reviews_db.values())

@app.post("/reviews", tags=["Reviews"])
def create_review(review: ReviewCreate):
    return review #devuelve reseña para confirmar

@app.put("/reviews/{reviewId}", tags=["Reviews"])
def update_review(reviewId: int) -> Review:
    return Review()

@app.delete("/reviews/{reviewId}", tags=["Reviews"])
def delete_review(reviewId: int):
    return 204 #simular la eliminación de una reseña



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
