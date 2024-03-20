"""import os
import uuid

from fastapi import APIRouter, HTTPException, status, Request, Form, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.websockets import WebSocket
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

from dotenv import load_dotenv
#from agora_token_builder.AccessToken import AccessToken  
#from agora_token_builder.RtcTokenBuilder import RtcTokenBuilder, Role_Publisher, Role_Subscriber
from datetime import datetime, timedelta
from router.socket_manager import manager
from router.websocket import websocket_endpoint

load_dotenv()

routeagora = APIRouter(tags=["agora"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

load_dotenv()

async def generate_token(channel_name, uid):
    try:
        token = RtcTokenBuilder.build_token_with_uid(os.getenv("APP_ID"),
                                                     os.getenv("APP_CERTIFICATE"),channel_name,0, Role_Publisher,3600)
        return token
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al generar el token: {str(e)}") 

async def handle_websocket_message(websocket: WebSocket, message: str):
    # Aquí puedes agregar la lógica para procesar el mensaje recibido
    # Por ejemplo, puedes imprimirlo o realizar alguna acción en función del contenido del mensaje
    print(f"Mensaje recibido: {message}")
    
    # También puedes enviar una respuesta al cliente si es necesario
    await websocket.send_text("Mensaje recibido correctamente")


@routeagora.post("/api/user/createroom", status_code=status.HTTP_201_CREATED)
async def create_room(patient_id: int, websocket: WebSocket = None, current_user: str = Depends(get_current_user)):
    try:
        date = datetime.now()
        formdate = date.strftime("%d/%m/%Y")
        room_id = str(f"paciente {patient_id} {formdate}")
        token = await generate_token(room_id, patient_id)
        with engine.connect() as conn:
            uid = conn.execute(users.select().where(users.c.id == patient_id)).first()
            if not uid:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el paciente")
            conn.execute(agora_rooms.insert().values(channel_name=room_id, user_id_creator=patient_id, entrance=False, token=token))
            print("inserta la sala")
            conn.commit()
        await manager.broadcast(f"New call created by patient {patient_id}")
        if websocket:
            await websocket.send_text(f"Nueva llamada creada por el paciente {patient_id}")
        return JSONResponse(content={"message": "Room created successfully"})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error al crear la sala de llamada: {str(e)}")
    

@routeagora.get("/doctor/listvideocall")
async def list_video_call(skip: int = 0, limit: int = 25, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn: 
        pend_vc = conn.execute(select(users.c.id, 
                                       users.c.name, 
                                       users.c.last_name, 
                                       users.c.birthdate,
                                       agora_rooms.c.channel_name).
                                select_from(agora_rooms).
                                join(users, agora_rooms.c.user_id_creator==users.c.id).                               
                                where(agora_rooms.c.entrance==False).order_by(agora_rooms.c.created_at.asc())
                                .offset(skip)
                                .limit(limit)).fetchall()
    if not pend_vc: 
        return JSONResponse(content={
            "message": "No hay pacientes en espera de consulta"
        }, status_code=status.HTTP_404_NOT_FOUND)
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

@routeagora.get("/doctor/joinroom/", status_code=status.HTTP_200_OK)
async def join_room(channel_name: str, current_user: str = "andresprueba@yopmail.com"):
    try:
        with engine.connect() as conn:
            room_exist = conn.execute(agora_rooms.select().where(agora_rooms.c.channel_name==channel_name).
                                      where(agora_rooms.c.entrance==False)).first() 
            print("hace la consulta de sala")
            if room_exist is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La sala de llamada no existe.")
            doctor_id = conn.execute(select(users.c.id).select_from(users).where(users.c.email==current_user)).first()
            print("consulta el id del doctor: ", doctor_id[0])
            conn.execute(agora_rooms.update().where(agora_rooms.c.id==room_exist.id).values(entrance=True, user_id_invite=doctor_id[0]))
            conn.commit()
            data_channel = conn.execute(select(agora_rooms.c.token, agora_rooms.c.channel_name).select_from(agora_rooms)
                                        .where(agora_rooms.c.id==room_exist.id)).first()
        if WebSocket:
            await manager.broadcast(f"Doctor {current_user} joined call in room {channel_name}")
        return {
            "token": data_channel.token,
            "channel_name": data_channel.channel_name
        } 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No se pudo unir a la sala de llamada: {str(e)}")"""

































import os  # Importar el módulo os para acceder a las variables de entorno
from fastapi import APIRouter, HTTPException, status, WebSocket, Form
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
    room_id = str(f"paciente {patient_id}")
    token = await generate_token(room_id, patient_id)
    with engine.connect() as conn:
      uid = conn.execute(users.select().where(users.c.id == patient_id)).first()
      if not uid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el paciente")
       
      conn.execute(agora_rooms.insert().values(channel_name=room_id, user_id_creator=patient_id, entrance=False, token=token))
      print("inserta la sala")
      conn.commit()
    
    return {
      "token": token,
      "room_id": room_id
    }
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error al crear la sala de llamada: {str(e)}")

@routeagora.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
        """  if data == "join_room":
                # Lógica para unirse a la sala aquí
                try:
                    room_id = await websocket.receive_text()
                    
                    if not room_id:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Falta el parámetro 'room_id'.")
                    
                    with engine.connect() as conn:
                        room_exist = conn.execute(
                            agora_rooms.select()
                            .where(agora_rooms.c.channel_name == room_id)
                            .where(agora_rooms.c.entrance == False)
                        ).first()
                        
                        if not room_exist:
                            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La sala de llamada no existe.")
                        
                        current_user = websocket.query_params.get("current_user")
                        
                        if not current_user:
                            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Falta el parámetro 'current_user'.")
                        
                        doctor_id = conn.execute(
                            select(users.c.id)
                            .where(users.c.email == current_user)
                        ).first()
                        
                        if not doctor_id:
                            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe.")
                        
                        conn.execute(
                            agora_rooms.update()
                            .where(agora_rooms.c.id == room_exist.id)
                            .values(entrance=True, user_id_invite=doctor_id[0])
                        )
                        conn.commit()
                        data_channel = conn.execute(
                            select(agora_rooms.c.token, agora_rooms.c.channel_name)
                            .where(agora_rooms.c.id == room_exist.id)
                        ).first()
                        await websocket.send_text("El usuario se ha unido a la sala exitosamente.")
                except Exception as e:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No se pudo unir a la sala de llamada: {str(e)}")
    except Exception as e:
        print(f"WebSocket connection closed with error: {str(e)}") """
