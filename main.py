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


#1 Modelos para REVIEWS - - - 
class Review(BaseModel):
    '''Modelo que representa una reseña'''
    id: str
    bookId: str
    userId: str
    comment: str
    rating: int

class ReviewCreate(BaseModel):
    '''Modelo para crear una reseña'''
    bookId: str
    userId: str
    comment: str
    rating: int

class ReviewUpdate(BaseModel): 
    '''Campos opcionales para actualizar solo lo que se desee'''
    comment: str | None = None  # Opcional
    rating: int | None = None   # Opcional
    

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


#2 Nuevos datos para Simular BD Reviews - - - - - 
reviews_db = {
    "1": {"id": "1", 
          "bookId": "101", 
          "userId": "user_1", 
          "comment": "Excelente libro", 
          "rating": 5
          },
    "2": {"id": "2", 
          "bookId": "102", 
          "userId": "user_2", 
          "comment": "El final estuvo confuso", 
          "rating": 2
          }
}
next_review_id = 3


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
    """Retorna todas las reseñas registradas"""
    return list(reviews_db.values())


@app.post("/reviews", response_model=Review, status_code=status.HTTP_201_CREATED, tags=["Reviews"])
def create_review(review_input: ReviewCreate):
    """Crea una nueva reseña y le asigna un ID"""
    global next_review_id
    new_id = str(next_review_id) #el usuario no crea un ID se genera atm
    
    new_review = {"id": new_id, **review_input.dict()} #crear un objeto uniendo el ID generado con los datos ingresados
    reviews_db[new_id] = new_review #se guarda el Id en el diccionario de BD simulada
    next_review_id += 1 #actualizar el contador de reviews

    return new_review


@app.put("/reviews/{review_id}", response_model=Review, tags=["Reviews"])
def update_review(review_id: str, review_input: ReviewUpdate):
    """Actualizar una reseña existente"""
    if review_id not in reviews_db: #Verificar si ya existe una reseña para actualizar
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    
    stored_review = reviews_db[review_id] #Para obtener los datos actuales (ya guardados)

    update_data = review_input.model_dump(exclude_unset=True) 
    updated_item = {**stored_review, **update_data} # nuevo dict 

    reviews_db[review_id] = updated_item

    return updated_item


@app.delete("/reviews/{review_id}", tags=["Reviews"])
def delete_review(review_id: str):
    """Eliminar una reseña"""
    if review_id not in reviews_db:
        raise HTTPException(status_code=404, detail="No hay una reseña con ese ID")
    
    del reviews_db[review_id]
    
    return {"message": "Reseña eliminada correctamente"} #200



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
