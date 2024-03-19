import os
import uuid
import requests

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

from dotenv import load_dotenv
#from agora_token_builder.AccessToken import AccessToken  
#from agora_token_builder.RtcTokenBuilder import RtcTokenBuilder, Role_Publisher, Role_Subscriber
from datetime import datetime, timedelta
from requests import post

load_dotenv()

routeagora = APIRouter(tags=["agora"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

async def generate_token(channel_name, uid):
    try:
       
        token = RtcTokenBuilder.build_token_with_uid(os.getenv("APP_ID"),
                                                     os.getenv("APP_CERTIFICATE"),channel_name,0, Role_Publisher,3600)
        return token
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al generar el token: {str(e)}") 

@routeagora.post("/api/user/createroom", status_code=status.HTTP_201_CREATED)
async def create_room(patient_id: int = Form(...)):
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

@routeagora.get("/doctor/listvideocall")
async def list_video_call(current_user: str = Depends(get_current_user)):
    with engine.connect() as conn: 
        pend_vc = conn.execute(select(users.c.id, 
                                       users.c.name, 
                                       users.c.last_name, 
                                       users.c.birthdate,
                                       agora_rooms.c.channel_name).
                                select_from(agora_rooms).
                                join(users, agora_rooms.c.user_id_creator==users.c.id).                               
                                where(agora_rooms.c.entrance==False)).fetchall()
        print(pend_vc)
    list_calls = [
        {
            "id": row[0],
            "name": row[1],
            "last_name": row[2],
            "birthdate": row[3],
            "channel_name": row[4]
        }
        for row in pend_vc
    ]
    return list_calls

@routeagora.get("/doctor/joinroom/")
async def join_room(channel_name: str, current_user: str = Depends(get_current_user)):
    try:
        with engine.connect() as conn:
            romm_exist = conn.execute(agora_rooms.select().where(agora_rooms.c.channel_name==channel_name)).first() 
            if romm_exist is None:
                raise HTTPException(status_code=404, detail="La sala de llamada no existe.")
            doctor_id = conn.execute(select(users.c.id).select_from(users).where(users.c.email==current_user)).first()
        token = RtcTokenBuilder.build_token_with_uid(os.getenv("APP_ID"),
                                                     os.getenv("APP_CERTIFICATE"),channel_name,0, Role_Subscriber,3600)
        return token
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No se pudo unir a la sala de llamada: {str(e)}")