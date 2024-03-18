from jose import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict
from fastapi import APIRouter, status, HTTPException
import requests

routezoom = APIRouter(tags=["Zoom"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

# Clave secreta para firmar el token
SECRET_KEY = "nb5TDfWHjS6qCnO6f02eO5YnVhDgxAzJIVdM"

# Función para generar un token JWT
def generar_token(api_key: str, api_secret: str, user_id: str, meeting_number: str, role: int) -> Dict[str, str]:
    # Payload del token
    payload = {
        "iss": api_key,
        "exp": datetime.utcnow() + timedelta(hours=1),  # Expiración en 1 hora
        "meeting_number": meeting_number,
        "user_id": user_id,
        "role": role,
    }

    # Firmar el token
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # Devolver el token y la clave
    return {"token": token}

# Función para crear una sala en Zoom Video SDK
def crear_sala_zoom_sdk(token: str, topic: str, user_id: str) -> dict:
    url = f"https://api.zoom.us/v2/users/{user_id}/meetings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "topic": topic
    }
    response = requests.post(url, headers=headers, json=data)
    print(response)
    if response.status_code == status.HTTP_201_CREATED:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

# Ruta para generar un token y crear una sala en Zoom Video SDK
@routezoom.post("/crear_sala_zoom_sdk")
async def crear_sala_zoom_sdk_endpoint(api_key: str, api_secret: str, user_id: str, role: int, topic: str):
    # Generar token
    token_info = generar_token(api_key, api_secret, user_id, role, topic)
    token = token_info["token"]
    
    # Crear sala en Zoom Video SDK
    meeting_info = crear_sala_zoom_sdk(token, topic, user_id)
    
    return {"token_info": token_info, "meeting_info": meeting_info}
