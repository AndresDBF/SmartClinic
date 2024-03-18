import os
import uuid
import requests
from requests import post
from fastapi import APIRouter, HTTPException, status, Request, Form
from config.db import engine
from model.user import users
from model.agora_rooms import agora_rooms
from router.logout import get_current_user
from schema import agora
from dotenv import load_dotenv
from agora_token_builder.AccessToken import AccessToken  
from agora_token_builder.RtcTokenBuilder import RtcTokenBuilder, Role_Publisher, Role_Subscriber
from datetime import datetime, timedelta

load_dotenv()

routeagora = APIRouter(tags=["agora"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

channel_name = "007eJxTYMhuv9qy+9m0E/0HOyeaZn5g/npzym9Llbvdq77E2a6IDdiiwJBmnGxgbmhslpJiYGJiYWiZaGlhYpyWkpiUbJJsYGpiojb3S2pDICOD7D4uRkYGCATx2RkKikpTkxINGRgAqNgi1w=="
@routeagora.post("/generate-token/")
async def generate_token():
    try:
        expires = datetime.utcnow() +  timedelta(minutes=15)

        token = AccessToken(os.getenv("APP_ID"), 
                            os.getenv("APP_CERTIFICATE"),
                            channel_name,
                            0).build()
        
 
        return {"token": token, "channel_name": channel_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al generar el token: {str(e)}") 


    
@routeagora.post("/regenerate_channel_token/") 
async def regenerate_channel_token():
    try:
        token_builder = RtcTokenBuilder()
        token = token_builder.buildTokenWithUid(os.getenv("APP_ID"), os.getenv("APP_CERTIFICATE"),
                                                channel_name, 0, Role_Publisher, 0)
        return {"token": token, "channel_name": channel_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al generar el token del canal: {str(e)}")

@routeagora.post("/create-room")
async def create_room(creator_id: str = Form(...), invite_id: str = Form(...)):
    
    try:
        with engine.connect() as conn:
            us_exist = conn.execute(users.select().where(users.c.id.in_([creator_id, invite_id]))).fetchall()
            if len(us_exist) != 2:
                raise HTTPException(status_code=404, detail="Al menos uno de los usuarios no existe.")
            room_id = str(uuid.uuid4())
            conn.execute(agora_rooms.insert().values(id=room_id, creator_id=creator_id, invitee_id=invite_id))
            conn.commit()
        return {"room_id": room_id, "creator_id": creator_id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error al crear la sala de llamada: {str(e)}")

@routeagora.get("/join-room/{room_id}")
async def join_room(room_id: str):
    try:
        with engine.connect() as conn:
            romm_exist = conn.execute(agora_rooms.select().where(agora_rooms.c.room_id == room_id)).first() 
        if romm_exist is None:
            raise HTTPException(status_code=404, detail="La sala de llamada no existe.")
        token_builder = RtcTokenBuilder()
        token = token_builder.buildTokenWithUid(os.getenv("APP_ID"), os.getenv("APP_CERTIFICATE"),
                                                os.getenv("CHANNEL_NAME"), romm_exist.user_id_invite, Role_Subscriber, 0)
        return {"room_id": room_id, "token": token}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No se pudo unir a la sala de llamada: {str(e)}")
    
     
    