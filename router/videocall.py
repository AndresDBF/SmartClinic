from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from jose import jwt
from zoomus import ZoomClient
import requests
import json

routezoom = APIRouter(tags=["Zoom"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})
"""
# Simulación de base de datos para almacenar la información de las salas creadas
rooms_db = []

# Configura las credenciales de la aplicación Zoom
CLIENT_ID = "6KcbASXNTT2CUns1gnTlgA"
CLIENT_SECRET = "nb5TDfWHjS6qCnO6f02eO5YnVhDgxAzJIVdM"

# URL de la API de Zoom para obtener el token de acceso
token_url = "https://zoom.us/oauth/token"


data = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}


def get_access_token():
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
        return response.json()["access_token"]
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el token de acceso: {str(e)}")


def create_room(topic: str) -> dict:
    access_token = get_access_token()
    print("el token de acceso generado es: ", access_token)
    #token = jwt.decode(access_token, CLIENT_SECRET, algorithms='HS256')
    
    #print("este es el token decode: ", token)
    #print("este es el nuevo token: ", new_token)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "role_type": 2,
        "topic": topic,   
    }

    print(headers)
    print(data)

    try:
        response = requests.post("https://api.zoom.us/v2/metrics/meetings", headers=headers, json=data)
        print(response)
        response.raise_for_status()  
       
        meeting_info = response.json()
        room_id = meeting_info.get("id")
        room_token = meeting_info.get("password")
        expiry_time = datetime.utcnow() + timedelta(minutes=30)  # Token válido por 30 minutos
        room_info = {"room_id": room_id, "room_token": room_token, "expiry_time": expiry_time}
        rooms_db.append(room_info)
        return room_info 
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la sala en Zoom: {str(e)}")

def is_token_expired(room_id: str) -> bool:
    for room in rooms_db:
        if room["room_id"] == room_id:
            return datetime.utcnow() > room["expiry_time"]
    return True

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




# Función para generar un token JWT válido para Zoom
def generate_zoom_token() -> str:
    # Calcula el tiempo de expiración del token (30 minutos desde ahora)
    exp_time = datetime.utcnow() + timedelta(minutes=30)
    # Construye el payload del token
    payload = {
        "app_key": CLIENT_ID,
        "role_type": 1,
        "tpc": "prueba",
        "version": 1,
        "iat": datetime.utcnow(),
        "exp": exp_time
    }
    # Genera el token JWT con el payload y firma utilizando HMAC con SHA-256
    token = jwt.encode(payload, CLIENT_ID, algorithm='HS256')
    return token

# Ruta para crear una sala y obtener su token
@routezoom.post("/crear_sala/")
async def crear_sala(topic: str):
    # Genera el token JWT para autenticación en la API de Zoom
    access_token = generate_zoom_token()
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
    # Realiza la solicitud POST a la API de Zoom para crear la sala
    try:
        response = requests.post("https://api.zoom.us/v2/users/me/meetings", headers=headers, json=data)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
        meeting_info = response.json()
        room_id = meeting_info.get("id")
        room_token = meeting_info.get("password")
        expiry_time = datetime.utcnow() + timedelta(minutes=30)  # Token válido por 30 minutos
        room_info = {"room_id": room_id, "room_token": room_token, "expiry_time": expiry_time}
        rooms_db.append(room_info)
        return room_info
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la sala en Zoom: {str(e)}")
    
    
    
    
    
     """