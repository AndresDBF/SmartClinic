import os
from fastapi import APIRouter, Response, status, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config.db import engine

from model.user import users
from model.usercontact import usercontact
from model.images.user_image_profile import user_image_profile

from model.images.user_image_profile import user_image_profile

from router.paciente.home import get_current_user
from router.paciente.user import SECRET_KEY, ALGORITHM


from sqlalchemy import insert, select, func, or_, and_
from sqlalchemy.exc import IntegrityError

from starlette.requests import Request

from os import getcwd, remove

from jose import jwt, JWTError


security = HTTPBearer()
# Obtener la ruta absoluta del directorio raíz del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
luser = APIRouter(tags=["Admin Verify User"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

img_directory = os.path.abspath(os.path.join(project_root, 'SmartClinic', 'img', 'profile'))


luser.mount("/img", StaticFiles(directory=img_directory), name="img")

@luser.get("/admin/listusers")
async def list_users(request: Request):
    with engine.connect() as conn:
        # Obtener usuarios sin verificar
        users_query = conn.execute(users.select().join(user_image_profile, users.c.id == user_image_profile.c.user_id).
                                   where(users.c.verify_ident==1).
                                   where(users.c.disabled==1)).fetchall()
        
        # Verificar si se encontraron usuarios sin verificar
        if not users_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se han encontrado usuarios para verificarse")

        # Obtener datos de usuario y de contacto
        list_user = [
            {
                "id": rowus[0],
                "username": rowus[1],
                "email": rowus[2],
                "name": rowus[4],
                "last_name": rowus[5],
                "gender": rowus[6],
                "birthdate": rowus[7],
                "tipid": rowus[8],
                "identification": rowus[9],
                "disabled": rowus[10],
                "verify_ident": rowus[11]
            }
            for rowus in users_query
        ]

        user_ids = [rowus[0] for rowus in users_query]  # Lista de IDs de usuarios

        # Obtener datos de contacto de usuario
        user_contact_query = usercontact.select().where(usercontact.c.user_id.in_(user_ids))
        user_contact_rows = conn.execute(user_contact_query).fetchall()

        list_user_contact = [
            {
                "user_id": rowusc[0],  # Agregar el ID del usuario
                "phone": rowusc[2],
                "country": rowusc[3],
                "state": rowusc[4],
                "direction": rowusc[5]
            }
            for rowusc in user_contact_rows
        ]

        # Combinar datos de usuario y contacto
        data_list = []
        for userdata in list_user:
            user_id = userdata["id"]
            user_contact_data = next((usercdata for usercdata in list_user_contact if usercdata["user_id"] == user_id), None)
            if user_contact_data:
                full_user_data = {**userdata, **user_contact_data}
            else:
                full_user_data = userdata
            # Obtener la imagen del perfil del usuario
            image_row = conn.execute(user_image_profile.select().where(user_image_profile.c.user_id == user_id).order_by(user_image_profile.c.id.desc())  # Ordenar por ID de imagen descendente
            ).first()
            
            if image_row:
                file_path_prof = f"./img/profile/{image_row.image_profile}.png"
                if not os.path.exists(file_path_prof):
                    return {"error": "La imagen de perfil no existe"}

                prof_img = FileResponse(file_path_prof)
                base_url = str(request.base_url)
                image_url_prof = f"{base_url.rstrip('/')}/img/profile/{image_row.image_profile}.png"
                full_user_data["url_prof_img"] = image_url_prof
            else:
                full_user_data["url_prof_img"] = None
            data_list.append(full_user_data)
    return data_list


@luser.post("/admin/searchuser")
async def search_user(name: str,request: Request):
    with engine.connect() as conn:
        name_parts = name.split()
        print(name_parts)
        # Obtener el primer y último nombre
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        # Realizar la búsqueda combinada
        name_user = conn.execute(users.select().where(
            and_(
                users.c.name.like(f'%{first_name}%'),
                users.c.last_name.like(f'%{last_name}%')
            )
        ).where(
            or_(
                users.c.last_name.like(f'%{last_name}%'),
                users.c.name.like(f'%{first_name}%')
            ))).fetchall()
        if not name_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se han encontrado usuarios para verificarse")

        # Obtener datos de usuario y de contacto
        list_user = [
            {
                "id": rowus[0],
                "username": rowus[1],
                "email": rowus[2],
                "name": rowus[4],
                "last_name": rowus[5],
                "gender": rowus[6],
                "birthdate": rowus[7],
                "tipid": rowus[8],
                "identification": rowus[9]
            }
            for rowus in name_user
        ]

        user_ids = [rowus[0] for rowus in name_user]  # Lista de IDs de usuarios

        # Obtener datos de contacto de usuario
        user_contact_query = usercontact.select().where(usercontact.c.user_id.in_(user_ids))
        user_contact_rows = conn.execute(user_contact_query).fetchall()

        list_user_contact = [
            {
                "user_id": rowusc[0],  # Agregar el ID del usuario
                "phone": rowusc[2],
                "country": rowusc[3],
                "state": rowusc[4],
                "direction": rowusc[5]
            }
            for rowusc in user_contact_rows
        ]

        # Combinar datos de usuario y contacto
        data_list = []
        for userdata in list_user:
            user_id = userdata["id"]
            user_contact_data = next((usercdata for usercdata in list_user_contact if usercdata["user_id"] == user_id), None)
            if user_contact_data:
                full_user_data = {**userdata, **user_contact_data}
            else:
                full_user_data = userdata
            # Obtener la imagen del perfil del usuario
            image_row = conn.execute(user_image_profile.select().where(user_image_profile.c.user_id == user_id).order_by(user_image_profile.c.id.desc())  # Ordenar por ID de imagen descendente
            ).first()
            
            if image_row:
                file_path_prof = f"./img/profile/{image_row.image_profile}.png"
                if not os.path.exists(file_path_prof):
                    return {"error": "La imagen de perfil no existe"}

                prof_img = FileResponse(file_path_prof)
                base_url = str(request.base_url)
                image_url_prof = f"{base_url.rstrip('/')}/img/profile/{image_row.image_profile}.png"
                full_user_data["url_prof_img"] = image_url_prof
            else:
                full_user_data["url_prof_img"] = None
            data_list.append(full_user_data)
    return data_list