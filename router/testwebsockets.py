import os
from fastapi import APIRouter, WebSocket, status, HTTPException, Depends
from fastapi.responses import HTMLResponse
from typing import List
from config.db import engine

from model.user import users
from model.agora_rooms import agora_rooms
from model.tip_consult import tip_consult
from model.patient_consult import patient_consult
from model.experience_doctor import experience_doctor

from router.logout import get_current_user
from agora.RtcTokenBuilder2 import RtcTokenBuilder
from agora.RtcTokenBuilder2 import Role_Publisher, Role_Subscriber

from sqlalchemy import select, insert, func
from sqlalchemy.exc import IntegrityError

from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import jwt


router_websockets = APIRouter(tags=["agora"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

load_dotenv()

async def get_user_id_from_token(token: str) -> int:
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        email = payload.get("sub")
        if email:
            with engine.connect() as conn:
                user = conn.execute(select([users.c.id]).where(users.c.email == email)).first()
                if user:
                    return user[0]  
        return None  
    except Exception:
        return "Token invalido"  

@router_websockets.websocket("/ws/paciente/{patient_id}")
async def paciente(websocket: WebSocket, patient_id: int, authorization: str):
    await websocket.accept()
    user_id = await get_user_id_from_token(authorization)
    if not user_id:
        await websocket.close()
    await websocket_paciente_logic(websocket, patient_id)


@router_websockets.websocket("/ws/doctor/{channel_name}")
async def doctor(websocket: WebSocket, channel_name: str, authorization: str):
    await websocket.accept()
    user_id = await get_user_id_from_token(authorization)
    if not user_id:
        await websocket.close()    
    await websocket_doctor_logic(websocket, channel_name, authorization, doctor.id)

async def websocket_paciente_logic(websocket: WebSocket, patient_id: int):
    while True:

        data = await websocket.receive_text()
        try:
            room_id = str(f"paciente_{patient_id}")
            with engine.connect() as conn:
                uid = conn.execute(users.select().where(users.c.id == patient_id)).first()
                if not uid:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el paciente")
                
                token = await generate_token(room_id, patient_id)
                conn.execute(agora_rooms.insert().values(channel_name=room_id, user_id_creator=patient_id, entrance=False, token=token))
                conn.commit()
            await websocket.send_json({"token": token, "channel_name": room_id})
         
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error al crear la sala de llamada: {str(e)}")

async def websocket_doctor_logic(websocket: WebSocket, channel_name: str, authorization: int, doctor_id: int):
    while True:

        data = await websocket.receive_text()
        try:
            with engine.connect() as conn:
                romm_exist = conn.execute(agora_rooms.select().where(agora_rooms.c.channel_name==channel_name)).first() 
                if romm_exist is None:
                    raise HTTPException(status_code=404, detail="La sala de llamada no existe.")
                doctor_id = conn.execute(select(users.c.id).select_from(users).where(users.c.id==authorization)).first()
                conn.execute(agora_rooms.update().where(agora_rooms.c.id==romm_exist.id).values(entrance=True, user_id_invite=doctor_id[0]))
                conn.commit()
            token = RtcTokenBuilder.build_token_with_uid(os.getenv("APP_ID"),
                                                        os.getenv("APP_CERTIFICATE"),channel_name,0, Role_Subscriber,3600)
            websocket.send_json({"token": token})
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No se pudo unir a la sala de llamada: {str(e)}")
        
async def generate_token(channel_name, uid):
    try:
        token = RtcTokenBuilder.build_token_with_uid(os.getenv("APP_ID"),
                                                     os.getenv("APP_CERTIFICATE"),channel_name,0, Role_Publisher,3600)
        return token
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al generar el token: {str(e)}") 