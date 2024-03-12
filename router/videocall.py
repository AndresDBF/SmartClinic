from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
import os
import requests

routezoom = APIRouter(tags=["Zoom"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

# Simulación de base de datos para almacenar la información de las salas creadas
rooms_db = []

# Configura las credenciales de la aplicación Zoom
CLIENT_ID = "SdH90AlxTugZluZyHg0KQ"
CLIENT_SECRET = "bmk9hRrCI7PLtpjHTvu2hMVegOO2NGTU"

# URL de la API de Zoom para obtener el token de acceso
token_url = "https://zoom.us/oauth/token"

# Parámetros requeridos para solicitar el token de acceso
data = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

# Realiza la solicitud POST para obtener el token de acceso
response = requests.post(token_url, data=data)

# Comprueba si la solicitud fue exitosa
if response.status_code == 200:
    # Extrae el token de acceso del cuerpo de la respuesta
    access_token = response.json()["access_token"]
    print("Token de acceso:", access_token)
else:
    print("Error al obtener el token de acceso:", response.text)

# Función para crear una sala y generar un token de acceso válido
def create_room(topic: str) -> dict:
    print("entra a la funcion")
    print(access_token)
    # Configura los encabezados con el token de acceso
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    # Configura los datos de la solicitud para crear la sala
    data = {
        "topic": topic,
        "type": 2
    }
    print(headers)
    print(data)
    # Realiza la solicitud POST a la API de Zoom para crear la sala
    response = requests.post("https://api.zoom.us/v2/users/me/meetings", headers=headers, json=data)
    print(response)
    # Procesa la respuesta de la API de Zoom
    if response.status_code == 201:
        meeting_info = response.json()
        room_id = meeting_info.get("id")
        room_token = meeting_info.get("password")
        expiry_time = datetime.utcnow() + timedelta(minutes=30)  # Token válido por 30 minutos
        room_info = {"room_id": room_id, "room_token": room_token, "expiry_time": expiry_time}
        rooms_db.append(room_info)
        return room_info
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

# Función para verificar si el token de una sala ha expirado
def is_token_expired(room_id: str) -> bool:
    for room in rooms_db:
        if room["room_id"] == room_id:
            return datetime.utcnow() > room["expiry_time"]
    return True

# Ruta para crear una sala y obtener su token
@routezoom.post("/crear_sala/")
async def crear_sala(topic: str):
    room_info = create_room(topic)
    print(room_info)
    return room_info

# Ruta para unirse a una sala utilizando un token válido
@routezoom.get("/unirse_sala/{room_id}/{room_token}")
async def unirse_sala(room_id: str, room_token: str):
    for room in rooms_db:
        if room["room_id"] == room_id:
            if is_token_expired(room_id):
                raise HTTPException(status_code=404, detail="La sala no existe o el token ha expirado")
            if room_token != room["room_token"]:
                raise HTTPException(status_code=401, detail="Token de acceso inválido")
            # Implementa la lógica para unirse a la sala con el token proporcionado
            return {"message": "Te has unido a la sala exitosamente"}
    raise HTTPException(status_code=404, detail="La sala no existe")
