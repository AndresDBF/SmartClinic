from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form, Response, Depends
from fastapi.responses import JSONResponse
from config.db import engine
from model.user import users
from model.roles.user_roles import user_roles
from model.experience_doctor import experience_doctor
from model.usercontact import usercontact
from sqlalchemy import select, insert, func

from router.paciente.home import get_current_user

routedoc = APIRouter(tags=["Doctor"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@routedoc.get("/doctor/listdocs")
async def get_doctors(current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        data_doctors = conn.execute(users.select().
                                    join(user_roles, users.c.id == user_roles.c.user_id).
                                    where(user_roles.c.role_id==2)).fetchall()
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
    