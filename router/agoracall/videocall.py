""" from fastapi import APIRouter, status, HTTPException
from agora import RtcTokenBuilder, RtmTokenBuilder, RtcRole, RtmRole

agora = APIRouter(["Agora Call"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@agora.post("/handle_call")
def handle_call(request_data: dict):

    app_id = "f3c07136dd044819a9843fdabc4c0544"
    app_certificate = "9b0ba02c8db242c2a4d7a077fdba6c50"
    channel_name = request_data["prueba"]
    user_id = request_data["e56aac3b930c45509afdec3682ccd18b"]
    role = RtcRole.PUBLISHER  
    
    token = RtcTokenBuilder.buildTokenWithUid(app_id, app_certificate, channel_name, user_id, role)
    
    return {"token": token}


 
 
 
  """
 
 
 
 
 
 
 
 
 
 
 
""" 
 
 
 
import os
import time
from flask import render_template, jsonify, request
from flask_login import login_required, current_user

from . import agora
from ..models import User
from .agora_key.RtcTokenBuilder import RtcTokenBuilder, Role_Attendee
from pusher import Pusher


# Instantiate a Pusher Client
pusher_client = Pusher(app_id=os.environ.get('PUSHER_APP_ID'),
                       key=os.environ.get('PUSHER_KEY'),
                       secret=os.environ.get('PUSHER_SECRET'),
                       ssl=True,
                       cluster=os.environ.get('PUSHER_CLUSTER')
                       )

@agora.route('/')
@agora.route('/agora')
@login_required
def index():
    users = User.query.all()
    all_users = [user.to_json() for user in users]
    return render_template('agora/index.html', title='Video Chat', allUsers=all_users)


@agora.route('/agora/pusher/auth', methods=['POST'])
def pusher_auth():
    auth_user = current_user.to_json()
    payload = pusher_client.authenticate(
        channel=request.form['channel_name'],
        socket_id=request.form['socket_id'],
        custom_data={
            'user_id': auth_user['id'],
            'user_info': {
                'id': auth_user['id'],
                'name': auth_user['username']
            }
        })
    return jsonify(payload)


@agora.route('/agora/token',  methods=['POST'])
def generate_agora_token():
    auth_user = current_user.to_json()
    appID = os.environ.get('AGORA_APP_ID')
    appCertificate = os.environ.get('AGORA_APP_CERTIFICATE')
    channelName = request.json['channelName']
    userAccount = auth_user['username']
    expireTimeInSeconds = 3600
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

    token = RtcTokenBuilder.buildTokenWithAccount(
        appID, appCertificate, channelName, userAccount, Role_Attendee, privilegeExpiredTs)

    return jsonify({'token': token, 'appID': appID})


@agora.route('/agora/call-user',  methods=['POST'])
def call_user():
    auth_user = current_user.to_json()
    pusher_client.trigger(
        'presence-online-channel',
        'make-agora-call',
        {
            'userToCall': request.json['user_to_call'],
            'channelName': request.json['channel_name'],
            'from': auth_user['id']
        }
    )
    return jsonify({'message': 'call has been placed'})


"""















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