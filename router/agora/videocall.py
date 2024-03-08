from agora.videocall import RtcTokenBuilder, RtmTokenBuilder, RtcRole, RtmRole
from fastapi import FastAPI

app = FastAPI()

@app.post("/handle_call")
def handle_call(request_data: dict):

    app_id = "your_app_id"
    app_certificate = "your_app_certificate"
    channel_name = request_data["channel_name"]
    user_id = request_data["user_id"]
    role = RtcRole.PUBLISHER  
    
    token = RtcTokenBuilder.buildTokenWithUid(app_id, app_certificate, channel_name, user_id, role)
    
    return {"token": token}






















""" 

from fastapi import APIRouter, HTTPException, Depends, Header, status
from datetime import datetime, timedelta

from pydantic import BaseModel
from typing import Optional
from jose import jwt

   
routeagora = APIRouter(tags=["Video Call Agora"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})


# Secret key for encoding and decoding JWT tokens
SECRET_KEY = "04e7c0ad2b92e73b001b6318f3791e7338b03c362d59185463af639565c84e60"
ALGORITHM = "HS256"

# Mock database users and rooms
users_db = {
    1: {"id": 1, "email": "user@example.com", "password": "password123", "role": "patient"},
    # Add more users as needed
}

rooms_db = {
    "room1": {"id": "room1", "participants": []},
    # Add more rooms as needed
}

class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Function to authenticate user
def authenticate_user(email: str, password: str):
    user = next((user_info for user_info in users_db.values() if user_info["email"] == email), None)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return user

# Function to generate JWT token
def create_jwt_token(user_id: int, role: str, room_id: Optional[str] = None):
    data = {"user_id": user_id, "role": role}
    if room_id:
        data["room_id"] = room_id
    expires = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({"exp": expires, **data}, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Function to verify JWT token
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@routeagora.post("/login", response_model=Token)
async def login(user: User):
    authenticated_user = authenticate_user(user.email, user.password)
    token = create_jwt_token(authenticated_user["id"], authenticated_user["role"])
    return {"access_token": token, "token_type": "bearer"}

@routeagora.post("/create_room", response_model=Token)
async def create_room(user_id: int = Header(..., description="User ID"), role: str = Header(..., description="User Role")):
    if role != "patient":
        raise HTTPException(status_code=403, detail="Only doctors can create rooms")
    room_id = f"room{len(rooms_db) + 1}"
    rooms_db[room_id] = {"id": room_id, "participants": []}
    token = create_jwt_token(user_id, role, room_id)
    return {"access_token": token, "token_type": "bearer"}


@routeagora.post("/join_room/{room_id}")
async def join_room(room_id: str, token: str = Header(..., description="JWT Token")):
    payload = verify_jwt_token(token)
    user_id = payload["user_id"]
    role = payload["role"]
    room = rooms_db.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if role == "patient":
        if user_id not in room["participants"]:
            room["participants"].append(user_id)
    elif role == "doctor":
        room["participants"].append(user_id)
    else:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return {"message": f"User {user_id} joined room {room_id}"}
 """