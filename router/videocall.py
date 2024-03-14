import hmac
import hashlib
import json
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status

routezoom = APIRouter(tags=["Zoom"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

def generate_signature(sdk_key, sdk_secret, session_name, role, session_key, user_identity):
    iat = int(datetime.now().timestamp()) - 30
    exp = iat + 60 * 60 * 2

    payload = {
        "app_key": sdk_key,
        "tpc": session_name,
        "role_type": role,
        "session_key": session_key,
        "user_identity": user_identity,
        "version": 1,
        "iat": iat,
        "exp": exp
    }

    header = json.dumps({"alg": "HS256", "typ": "JWT"})
    payload = json.dumps(payload)

    token = header.encode('utf-8') + b'.' + payload.encode('utf-8')
    print(token)
    signature = hmac.new(sdk_secret.encode('utf-8'), token, hashlib.sha256).digest()
    print(signature)
    print("este es el sdk: ", sdk_secret)

    return token + b'.' + signature

@routezoom.get("/crearsala")
async def generate_jwt():
    sdk_key = os.getenv("6KcbASXNTT2CUns1gnTlgA")
    sdk_secret = os.getenv("nb5TDfWHjS6qCnO6f02eO5YnVhDgxAzJIVdM")

    session_name = "Cool Cars"
    role = 1
    session_key = "session123"
    user_identity = "user123"

    signature = generate_signature(sdk_key, sdk_secret, session_name, role, session_key, user_identity)
    return {"jwt": signature.decode('utf-8')}


""" from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from jose import jwt
from zoomus import ZoomClient
from time import time
import requests
import json

routezoom = APIRouter(tags=["Zoom"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

# Simulación de base de datos para almacenar la información de las salas creadas
rooms_db = []

# Configura las credenciales de la aplicación Zoom
CLIENT_ID = "6KcbASXNTT2CUns1gnTlgA"
CLIENT_SECRET = "nb5TDfWHjS6qCnO6f02eO5YnVhDgxAzJIVdM"

# URL de la API de Zoom para obtener el token de acceso
token_url = "https://zoom.us/oauth/token"

userId = 'you can get your user Id by running the getusers()'

data = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

try:
    response = requests.post(token_url, data=data)
    response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
    access_token = response.json()["access_token"]

    print("Token de acceso:", access_token)

except requests.RequestException as e:
    raise HTTPException(status_code=500, detail=f"Error al hacer la solicitud para obtener el token de acceso: {str(e)}")


def generateToken():
    token = jwt.encode(
        # Create a payload of the token containing API Key & expiration time
        {'iss': CLIENT_ID, 'exp': time() + 5000},
        # Secret used to generate token signature
        CLIENT_SECRET,
        # Specify the hashing alg
        algorithm='HS256'
        # Convert token to utf-8
    )
    print(token)
    return token

def get_access_token():
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
        return response.json()["access_token"]
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el token de acceso: {str(e)}")


def create_room(topic: str) -> dict:
    
    #token = jwt.decode(access_token, CLIENT_SECRET, algorithms='HS256')
    
    #print("este es el token decode: ", token)
    #print("este es el nuevo token: ", new_token)
    
    
   

    meetingdetails = {"topic": f"{topic}",
                  "type": 2,
                  "start_time": "2019-06-14T10: 21: 57",
                  "duration": "45",
                  "timezone": "Europe/Madrid",
                  "agenda": "test",

                  "recurrence": {"type": 1,
                                 "repeat_interval": 1
                                 },
                  "settings": {"host_video": "true",
                               "participant_video": "true",
                               "join_before_host": "False",
                               "mute_upon_entry": "False",
                               "watermark": "true",
                               "audio": "voip",
                               "auto_recording": "cloud"
                               }
                  }

    
    headers = {'authorization': 'Bearer %s' % generateToken(),
               'content-type': 'application/json'}
    r = requests.post(
        f'https://api.zoom.us/v2/users/me/meetings', headers=headers, data=json.dumps(meetingdetails))

    print("\n creating zoom meeting ... \n")
    return r.text
    

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
    
    
    
""" 
from jose import jwt
import requests
import json
from time import time

API_KEY = 'OpP9rLrvQui7sMJKp7jQjg'
API_SEC = 'flEJffgVBVgj3XSP8gl8QJJKwJNUR8Sh'

# your zoom live meeting id, it is optional though
meetingId = 83781439159

userId = 'you can get your user Id by running the getusers()'

# create a function to generate a token using the pyjwt library
def generateToken():
    token = jwt.encode(
        # Create a payload of the token containing API Key & expiration time
        {'iss': API_KEY, 'exp': time() + 5000},
        # Secret used to generate token signature
        API_SEC,
        # Specify the hashing alg
        algorithm='HS256'
        # Convert token to utf-8
    )
    return token
    # send a request with headers including a token

#fetching zoom meeting info now of the user, i.e, YOU
def getUsers():
    headers = {'authorization': 'Bearer %s' % generateToken(),
               'content-type': 'application/json'}

    r = requests.get('https://api.zoom.us/v2/users/', headers=headers)
    print("\n fetching zoom meeting info now of the user ... \n")
    print(r.text)


#fetching zoom meeting participants of the live meeting

def getMeetingParticipants():
    headers = {'authorization': 'Bearer %s' % generateToken(),
               'content-type': 'application/json'}
    r = requests.get(
        f'https://api.zoom.us/v2/metrics/meetings/{meetingId}/participants', headers=headers)
    print("\n fetching zoom meeting participants of the live meeting ... \n")

    # you need zoom premium subscription to get this detail, also it might not work as i haven't checked yet(coz i don't have zoom premium account)

    print(r.text)


# this is the json data that you need to fill as per your requirement to create zoom meeting, look up here for documentation
# https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingcreate


meetingdetails = {"topic": "The title of your zoom meeting",
                  "type": 2,
                  "start_time": "2019-06-14T10: 21: 57",
                  "duration": "45",
                  "timezone": "Europe/Madrid",
                  "agenda": "test",

                  "recurrence": {"type": 1,
                                 "repeat_interval": 1
                                 },
                  "settings": {"host_video": "true",
                               "participant_video": "true",
                               "join_before_host": "False",
                               "mute_upon_entry": "False",
                               "watermark": "true",
                               "audio": "voip",
                               "auto_recording": "cloud"
                               }
                  }

def createMeeting():
    headers = {'authorization': 'Bearer %s' % generateToken(),
               'content-type': 'application/json'}
    r = requests.post(
        f'https://api.zoom.us/v2/users/{userId}/meetings', headers=headers, data=json.dumps(meetingdetails))

    print("\n creating zoom meeting ... \n")
    print(r.text)

getUsers()
# getMeetingParticipants()
createMeeting() """