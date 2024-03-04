import random
import string
import os 
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config.db import engine

from model.user import users
from model.roles.user_roles import user_roles
from model.images.user_image import user_image
from model.experience_doctor import experience_doctor
from model.usercontact import usercontact
from model.person_antecedent import person_antecedent
from model.person_hobbie import person_hobbie
from model.family_antecedent import family_antecedent

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

@routedoc.get("/doctor/videocall/user/{user_id}")
async def get_info_user(user_id: int, request: Request):
    with engine.connect() as conn:
        user =  conn.execute(users.select().where(users.c.id == user_id)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el usuario")
            
        user_contact =  conn.execute(usercontact.select().where(usercontact.c.user_id==user_id)).first()
        
        number_of_strings = 5
        length_of_string = 9
        
        id = "#" + "".join(
                random.choice(string.ascii_letters + string.digits)
                for _ in range(length_of_string)
        )
        id = id.upper() 
        print(id)
        ant_per = conn.execute(person_antecedent.select().where(person_antecedent.c.user_id==user_id)).first()
        if ant_per is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron antecedentes del paciente")
        hobb_per = conn.execute(person_hobbie.select().where(person_hobbie.c.user_id==user_id)).first()
        fam_per = conn.execute(family_antecedent.select().where(family_antecedent.c.user_id==user_id)).first()
        
        image_row = conn.execute(user_image.select().where(user_image.c.user_id == user_id)).first()
        if image_row is not None:
            file_path_ident = f"./img/profile/{image_row.image_ident}.png"
            file_path_self = f"./img/profile/{image_row.image_self}.png"
            if not os.path.exists(file_path_ident):
                return {"error": "El archivo no existe"}
            if not os.path.exists(file_path_self):
                return {"error": "El archivo no existe"}
            
            image = FileResponse(file_path_ident)
            image = FileResponse(file_path_self)
            
            base_url = str(request.base_url)
            image_url_ident = f"{base_url.rstrip('/')}/img/profile/{image_row.image_ident}.png"
            image_url_self = f"{base_url.rstrip('/')}/img/profile/{image_row.image_self}.png"
            inf_patient = {
                "iduser": user[0],
                "id_ant": ant_per[0],
                "id_hob": hobb_per[0],
                "id_fper": fam_per[0],
                "username": user[1],
                "id_atent": id,
                "email": user[2],
                "name": user[4],
                "last_name": user[5],
                "birthdate": user[6],
                "gender": user[7],
                "tipid": user[8],
                "identification": user[9],
                "phone": user_contact[2],
                "country": user_contact[3],
                "state": user_contact[4],
                "direction": user_contact[5],
                "image_ident": image_url_ident,
                "image_self": image_url_self
            }
            return inf_patient
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron archivos de identidad del paciente")
        
@routedoc.get("/doctor/infomedic/")
async def get_inf_medic_patient(user_id: int, id_ant: int, id_hob: int, id_fper: int):
    pass