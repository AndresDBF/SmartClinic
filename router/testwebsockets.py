import os
from fastapi import APIRouter, HTTPException, status, Request, Form, Depends, Response
from fastapi.responses import JSONResponse
from config.db import engine

from model.user import users
from model.agora_rooms import agora_rooms
from model.tip_consult import tip_consult
from model.patient_consult import patient_consult

from router.logout import get_current_user
from agora.RtcTokenBuilder2 import RtcTokenBuilder
from agora.RtcTokenBuilder2 import Role_Publisher, Role_Subscriber

from sqlalchemy import select, insert, func
from sqlalchemy.exc import IntegrityError

from schema import agora

from websockets import connect

from dotenv import load_dotenv

load_dotenv()

routeagora = APIRouter(tags=["agora"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

async def generate_token(channel_name, uid):
    try:
    
        token = RtcTokenBuilder.build_token_with_uid(os.getenv("APP_ID"), os.getenv("APP_CERTIFICATE"),channel_name,0, Role_Publisher,3600)
        return token
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al generar el token: {str(e)}") 

@routeagora.post("/api/user/createroom", status_code=status.HTTP_201_CREATED)
async def create_room(patient_id: int):
    try:
        with engine.connect() as conn:
            uid = conn.execute(users.select().where(users.c.id == patient_id)).first()
        if not uid:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el paciente")
       
        room_id = str(f"paciente {patient_id}")
        conn.execute(agora_rooms.insert().values(channel_name=room_id, user_id_creator=patient_id, entrance=False))
        print("inserta la sala")
        conn.commit()
        token = await generate_token(room_id, patient_id)
        return {
            "token": token,
            "room_id": room_id
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error al crear la sala de llamada: {str(e)}")
@routeagora.get("/doctor/joinroom/", status_code=status.HTTP_200_OK)
async def join_room(channel_name: str, current_user: str = Depends(get_current_user)):
    try:
        with engine.connect() as conn:
            room_exist = conn.execute(agora_rooms.select().where(agora_rooms.c.channel_name == channel_name)
                                       .where(agora_rooms.c.entrance == False)).first()
            print("hace la consulta de sala")
            if room_exist is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La sala de llamada no existe.")

            doctor_id = conn.execute(select(users.c.id).select_from(users).where(users.c.email == current_user)).first()
            print("consulta el id del doctor: ", doctor_id[0])

            conn.execute(agora_rooms.update().where(agora_rooms.c.id == room_exist.id).values(entrance=True, user_id_invite=doctor_id[0]))
            conn.commit()

            data_channel = conn.execute(select(agora_rooms.c.token, agora_rooms.c.channel_name).select_from(agora_rooms)
                                         .where(agora_rooms.c.id == room_exist.id)).first()

            # Send notification to websocket channel (room specific)
            async with connect(f"ws://localhost:8000/ws/{channel_name}") as websocket:
                await websocket.send("doctor_joined")  # Message indicating doctor joined

            return {
                "token": data_channel.token,
                "channel_name": data_channel.channel_name
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No se pudo unir a la sala de llamada: {str(e)}")
async def detect_room(room_id: str):
    try:
        websocket = await connect(f"ws://localhost:8000/ws/{room_id}")
        async for message in websocket:
            if message == "entrance_true":
                # Existing logic for handling room creation
                await websocket.send("room_created")
            elif message == "doctor_joined":
                # Broadcast doctor joined message to all connected users
                await websocket.send(f"Doctor joined the call!")
            else:
                print("No se ha detectado ninguna acción")
    except Exception as e:
        print(f"Error al detectar la sala: {str(e)}")






# Se crea un endpoint para cada sala de videollamada
routeagora.websocket_route("/ws/{room_id}", detect_room)
