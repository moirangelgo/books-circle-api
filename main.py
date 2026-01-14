from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API de Clubes de Lectura",
    description="API REST para gestionar clubes de lectura",
    version="1.0.0"
)

# ============= MODELOS (Schemas) =============


# ------------Clubs--------------
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



#--------------------Meetings---------------------------
class Meeting(BaseModel):
    id: str
    bookId: Optional[str] = None
    bookTitle: Optional[str] = None
    scheduledAt: datetime
    duration: int
    location: Optional[str] = None
    locationUrl: Optional[str] = None
    description: Optional[str] = None
    createdBy: str
    attendeeCount: int
    status: str  # Próxima | Vencida | Cancelada
    isVirtual: bool
    virtualMeetingUrl: Optional[str] = None


class MeetingCreate(BaseModel):
    bookId: Optional[str] = None
    scheduledAt: datetime
    duration: int = Field(default=15, max_length=480)  #default valor mínimo max_leng valor máximo
    location: Optional[str] = Field(default=None, max_length=200)
    locationUrl: Optional[str] = None
    description: Optional[str] = Field(default=None, max_length=500)
    isVirtual: bool = False
    virtualMeetingUrl: Optional[str] = None


class MeetingUpdate(BaseModel):
    bookId: Optional[str] = None
    scheduledAt: datetime
    duration: Optional [int] = Field(ge=15, le=480)  #ge(greater o equal) valor mínimo le(less o equal) valor máximo
    location: Optional[str] = Field(default=None, max_length=200)
    locationUrl: Optional[str] = None
    description: Optional[str] = Field(default=None, max_length=500)
    isVirtual: bool = False
    virtualMeetingUrl: Optional[str] = None



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



#----------------DATOS ESTÁTICOS MEETINGS (SIMULACION BD)-------------------
meetings_db = {
    1: {
        "id": "mtg_1",
        "bookId": "bk_123abc",
        "bookTitle": "1984",
        "scheduledAt": "2026-01-25T18:00:00",
        "duration": 180,
        "location": "Biblioteca Vasconcelos",
        "locationUrl": None,
        "description": "Discusión de los primeros 5 capítulos",
        "createdBy": "usr_1",
        "attendeeCount": 5,
        "status": "Próxima",
        "isVirtual": False,
        "virtualMeetingUrl": None
    },
    2: {
        "id": "mtg_2",
        "bookId": None,
        "bookTitle": None,
        "scheduledAt": "2025-12-10T17:00:00",
        "duration": 30,
        "location": None,
        "locationUrl": None,
        "description": "Reunión virtual general",
        "createdBy": "usr_2",
        "attendeeCount": 3,
        "status": "Vencida",
        "isVirtual": True,
        "virtualMeetingUrl": "https://meet.google.com/"
        },
    3:{
        "id": "mtg_3",
        "bookId": "bk_123abc",
        "bookTitle": "1984",
        "scheduledAt": "2026-02-05T19:00:00",
        "duration": 120,
        "location": "Audiorama Parque México",
        "locationUrl": "https://maps.google.com/",
        "description": None,
        "createdBy": "usr_5",
        "attendeeCount": 8,
        "status": "Próxima",
        "isVirtual": False,
        "virtualMeetingUrl": None
        }
}

# Variable para generar IDs únicos
next_id = 4


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


#--------------------Meetings----------------

@app.get("/clubs{clubId}/meetings", response_model=list[Meeting], tags=["Meetings"])
def lista_reuniones(club_id: str):
    """
    Obtener todas las reuniones
    
    Retorna una lista con todas las reuniones registradas.
    """
    return list(meetings_db.get(club_id, []))

@app.post("/clubs{clubId}/meetings", response_model=Meeting, tags=["Meetings"])
def programar_reunión(club_id: int, meeting: MeetingCreate):
    return Meeting()

@app.get("/clubs/{clubId}/meetings/{meetingId}", tags=["Meetings"])
def obtener_detalles_de_reunión(meetingId: int) -> Meeting:
    return Meeting()


@app.put("/clubs/{clubId}/meetings/{meetingId}", tags=["Meetings"])
def actualizar_reunión(meetingId: int) -> Meeting:
    return Meeting()


@app.delete("/clubs/{clubId}/meetings/{meetingId}", tags=["Meetings"])
def cancelar_reunión(meetingId: int) -> int:
    return 204

@app.put("/clubs/{clubId}/meetings/{meetingId}/attendance", tags=["Meetings"])
def confirmar_asistencia(meetingId: int) -> Meeting:
    return Meeting()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

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