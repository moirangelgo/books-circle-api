# Documentación de Cambios - Feature: Members Management
**Fecha:** 14 de Enero, 2026
**Rama:** feature/members
**Autor:** GermanHv

## 1. Descripción General
Se ha implementado el módulo de gestión de **Miembros** dentro de la API de Clubes de Lectura. Esta funcionalidad permite asociar usuarios (miembros) a clubes específicos, visualizarlos y gestionar su ciclo de vida (creación y eliminación) mediante una estructura REST.

## 2. Cambios Técnicos Realizados

### A. Nuevos Modelos de Datos (Pydantic Schemas)
Se agregaron los siguientes esquemas para validación de datos:
* **`Member` (Response):** Define la estructura de salida de un miembro.
    * Campos: `id`, `name`, `email`, `joined_date`.
* **`MemberCreate` (Request):** Define los datos necesarios para registrar un miembro.
    * Campos: `name`, `email`.

### B. Persistencia de Datos (Simulación)
Se implementó `members_db`, un diccionario en memoria que simula una tabla relacional de base de datos.
* **Estructura:** `{ club_id: [ lista_de_objetos_miembro ] }`
* **Datos Semilla:** Se precargaron datos de prueba para los Clubes ID `1` y `2` para facilitar el testing inmediato sin necesidad de crear registros previos.

### C. Implementación de Endpoints
Se añadieron 3 nuevas rutas bajo el tag `Members`:

1.  **GET** `/clubs/{clubId}/members`
    * **Lógica:** Consulta `members_db` utilizando el ID del club.
    * **Comportamiento:** Retorna la lista de miembros si existen. Si el club no tiene miembros o no existe, retorna una lista vacía `[]` (Safe Response).
    
2.  **POST** `/clubs/{clubId}/members`
    * **Estado:** Estructura base implementada. Recibe el esquema `MemberCreate` y retorna el objeto recibido (Echo).
    
3.  **DELETE** `/clubs/{clubId}/members/{userId}`
    * **Estado:** Estructura base implementada. Retorna código HTTP `204 No Content`.

### D. Refactorización y Correcciones
* **Corrección de Nombres de Funciones:** En el archivo original, múltiples endpoints compartían el nombre de función `get_clubs`. Se renombraron las nuevas funciones (`get_members`, `create_member`, `delete_member`) para evitar conflictos en el enrutamiento de FastAPI.

## 3. Guía de Pruebas (Testing)

Para verificar la funcionalidad, se pueden realizar las siguientes peticiones:

**Caso 1: Obtener miembros de un club con datos (Club 1)**
* **URL:** `GET /clubs/1/members`
* **Resultado esperado:** JSON con 2 miembros ("Ana García", "Carlos Ruiz").

**Caso 2: Obtener miembros de un club vacío (Club 3)**
* **URL:** `GET /clubs/3/members`
* **Resultado esperado:** Lista vacía `[]`.

**Caso 3: Estructura de Creación**
* **URL:** `POST /clubs/1/members`
* **Body:** `{"name": "Test", "email": "test@mail.com"}`
* **Resultado esperado:** JSON con los mismos datos enviados.
