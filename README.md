# BookCircle API

![API Version](https://img.shields.io/badge/API%20Version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.85%2B-black)
![License](https://img.shields.io/badge/License-MIT-green)

API REST en **Python/FastAPI** para la gestión de clubes de lectura. Permite crear comunidades, proponer libros, organizar reuniones virtuales y compartir reseñas literarias.

## 📖 Tabla de Contenidos
- [Características Principales](#-características-principales)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación y Configuración](#-instalación-y-configuración)


## ✨ Características Principales
- **Gestión de clubes**: Creación de comunidades públicas/privadas con sistemas de membresía
- **Votación colaborativa**: Selección de libros mediante votaciones democráticas
- **Seguimiento de lectura**: Registro de progreso individual y colectivo
- **Calendario de reuniones**: Agendamiento de encuentros virtuales con recordatorios
- **Sistema de reputación**: Badges y reconocimientos por participación activa
- **Integración con ISBNdb**: Búsqueda automática de metadatos de libros

## ⚙️ Tecnologías Utilizadas
- **Framework**: FastAPI (ASGI)
- **Base de datos**: PostgreSQL + SQLAlchemy ORM
- **Autenticación**: OAuth2 con JWT
- **Testing**: pytest + TestClient
- **Documentación**: Swagger UI / ReDoc

## 🛠 Requisitos Previos
- Python 3.8+
- PostgreSQL 14+
- Virtualenv (`python -m venv venv`)

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/bookcircle/api.git
cd api
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# venv\Scripts\activate  # Windows
```
### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```


📄 Licencia
Distribuido bajo la licencia MIT.


