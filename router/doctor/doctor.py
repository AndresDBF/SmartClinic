import random
import string
import os 
from fastapi import APIRouter, HTTPException, status, Depends, Request, Form
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config.db import engine

from model.user import users
from model.roles.user_roles import user_roles
from model.images.user_image import user_image
from model.images.user_image_profile import user_image_profile
from model.experience_doctor import experience_doctor
from model.usercontact import usercontact
from model.person_antecedent import person_antecedent
from model.person_habit import personal_habit
from model.family_antecedent import family_antecedent
from model.inf_medic import inf_medic

from sqlalchemy import select, insert, func
from sqlalchemy.sql import select

from router.paciente.home import get_current_user
from router.roles.user_roles import verify_rol

routedoc = APIRouter(tags=["Video Call Doctor"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@routedoc.get("/doctor/listdocs")
async def get_doctors(current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        data_doctors = conn.execute(users.select().
                                    join(user_roles, users.c.id == user_roles.c.user_id).
                                    where(user_roles.c.role_id==2)).fetchall()
        if data_doctors is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay doctores registrados")
        experience = conn.execute(experience_doctor.select().
                                    join(users, experience_doctor.c.user_id==users.c.id).
                                    join(user_roles, users.c.id==user_roles.c.user_id).
                                    where(user_roles.c.role_id==2)).fetchall()
        data_doctors_contact = conn.execute(usercontact.select().
                                    join(users, usercontact.c.user_id == users.c.id).
                                    join(user_roles, users.c.id == user_roles.c.user_id).
                                    where(user_roles.c.role_id==2)).fetchall()
        # Combinar los resultados en un solo diccionario     
        
        list_docts = []
        for doctor, exp, contact in zip(data_doctors, experience, data_doctors_contact):
            list_docts.append({
                "id": doctor[0],
                "name": doctor[4],
                "email": doctor[2],
                "last_name": doctor[5],
                "phone": contact[2],
                "country": contact[3],
                "state": contact[4],
                "direction": contact[5],
                "name_exper": exp[2]
            })
    return list_docts

@routedoc.get("/doctor/assigndoc/")
async def assign_doctor(request: Request, user_id: int, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        veri_user = conn.execute(users.select().where(users.c.id==user_id)).first()
        if veri_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe")
        doctor = conn.execute(users.select().join(user_roles, users.c.id==user_roles.c.user_id)
                              .where(users.c.id==user_id).where(user_roles.c.role_id==3)).first()
        if doctor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El Usuario no es un doctor")
        doc_contact = conn.execute(usercontact.select().where(usercontact.c.user_id==user_id)).first()
        
        image_row = conn.execute(user_image_profile.select().where(user_image_profile.c.user_id == user_id)).first()
        if image_row is not None:
            file_path = f"./img/profile/{image_row.image_profile}.png"
            if not os.path.exists(file_path):
                return {"error": "El archivo no existe"}
            
            image = FileResponse(file_path)
            
            base_url = str(request.base_url)
            image_url = f"{base_url.rstrip('/')}/img/profile/{image_row.image_profile}.png"
        # Obtener datos de usuario y de contacto
        list_user = [
            {
                "id": doctor[0],
                "username": doctor[1],
                "email": doctor[2],
                "name": doctor[4],
                "last_name": doctor[5],
                "gender": doctor[6],
                "birthdate": doctor[7],
                "tipid": doctor[8],
                "identification": doctor[9],
                "phone": doc_contact[2],
                "country": doc_contact[3],
                "state": doc_contact[4],
                "direction": doc_contact[5],
                "url_img_profile": image_url
            }
        ]
    return list_user
