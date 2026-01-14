from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import uuid
import secrets

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API de Clubes de Lectura",
    description="API REST para gestionar clubes de lectura",
    version="1.0.0"
)

# ============= MODELOS (Schemas) =============
# Modelos de dominio base del proyecto creados por @osdroix

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


# ============= AUTENTICACIÓN (Schemas y utilidades) =============
# Modelos y helpers para los endpoints de autenticación añadidos con @osdroix


class RegisterInput(BaseModel):
    email: EmailStr
    password: str
    username: str
    fullName: str


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    fullName: str
    avatarUrl: str | None = None
    createdAt: datetime


users_db: dict[str, dict] = {}
tokens_db: dict[str, dict] = {}


def generate_user_id() -> str:
    return f"usr_{uuid.uuid4().hex[:8]}"


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def find_user_by_email(email: str) -> dict | None:
    for user in users_db.values():
        if user["email"] == email:
            return user
    return None


def find_user_by_username(username: str) -> dict | None:
    for user in users_db.values():
        if user["username"] == username:
            return user
    return None


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

# Variable para generar IDs únicos para clubs creada inicialmente por @osdroix
next_id = 4


# ============= ENDPOINTS =============

@app.get("/")
def root():
    """Endpoint raíz - Bienvenida"""
    return {
        "mensaje": "Bienvenido a la API de Clubes de Lectura",
        "documentacion": "/docs"
    }


# Endpoints principales de Clubs implementados por @osdroix
@app.get("/clubs", response_model=list[Club], tags=["Clubs"])
def get_clubs():
    """
    Obtener todos los clubes de lectura
    
    Retorna una lista con todos los clubes registrados.
    """
    return list(clubs_db.values())


# Endpoint de registro de usuarios (Auth) implementado junto con @osdroix
@app.post("/auth/register", tags=["Auth"], status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterInput):
    existing_email = find_user_by_email(payload.email)
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )
    existing_username = find_user_by_username(payload.username)
    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El username ya está registrado",
        )
    user_id = generate_user_id()
    now = datetime.utcnow()
    user_record = {
        "id": user_id,
        "email": payload.email,
        "username": payload.username,
        "fullName": payload.fullName,
        "avatarUrl": None,
        "createdAt": now,
        "password": payload.password,
    }
    users_db[user_id] = user_record
    token = generate_token()
    expires_in = 60 * 60 * 24
    tokens_db[token] = {
        "user_id": user_id,
        "expires_at": now + timedelta(seconds=expires_in),
    }
    user = User(
        id=user_record["id"],
        email=user_record["email"],
        username=user_record["username"],
        fullName=user_record["fullName"],
        avatarUrl=user_record["avatarUrl"],
        createdAt=user_record["createdAt"],
    )
    return {
        "user": user,
        "token": token,
    }


# Endpoint de login de usuarios (Auth) implementado junto con @osdroix
@app.post("/auth/login", tags=["Auth"])
def login_user(payload: LoginInput):
    user = find_user_by_email(payload.email)
    if user is None or user["password"] != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    token = generate_token()
    expires_in = 60 * 60 * 24
    now = datetime.utcnow()
    tokens_db[token] = {
        "user_id": user["id"],
        "expires_at": now + timedelta(seconds=expires_in),
    }
    user_model = User(
        id=user["id"],
        email=user["email"],
        username=user["username"],
        fullName=user["fullName"],
        avatarUrl=user["avatarUrl"],
        createdAt=user["createdAt"],
    )
    return {
        "user": user_model,
        "token": token,
        "expiresIn": expires_in,
    }


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



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
