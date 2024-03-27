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

from router.logout import get_current_user
from router.roles.roles import verify_rol_admin


from sqlalchemy import insert, select, func, or_, and_
from sqlalchemy.exc import IntegrityError

from starlette.requests import Request

from os import getcwd, remove

from jose import jwt, JWTError
from typing import Optional

security = HTTPBearer()
# Obtener la ruta absoluta del directorio raíz del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
luser = APIRouter(tags=["Admin Routes"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

img_directory = os.path.abspath(os.path.join(project_root, 'SmartClinic', 'img', 'profile'))


luser.mount("/img", StaticFiles(directory=img_directory), name="img")


#CONVERSAR CON EL FRONT COMO SE MANEJARA LOS USUARIOS EN LA LISTA DE "RECIENTES"

@luser.get("/admin/list-users/")
async def list_users(request: Request, current_user: str = Depends(get_current_user), search_query: Optional[str] = None):
    verify_rol_admin(current_user)
        
    with engine.connect() as conn:
        if search_query:  # Si hay una cadena de búsqueda
            
            name_parts = search_query.split()
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

            query = users.select().where(
                or_(
                    and_(
                        users.c.name.like(f'%{first_name}%'),
                        users.c.last_name.like(f'%{last_name}%')
                    ),
                    and_(
                        users.c.last_name.like(f'%{last_name}%'),
                        users.c.name.like(f'%{first_name}%')
                    ),
                    users.c.name.like(f'%{search_query}%'),
                    users.c.last_name.like(f'%{search_query}%')
                )
            )
            users_query = conn.execute(query).fetchall()
            print("entra en el primer if: ", users_query)
        else:  # Si no hay cadena de búsqueda, obtener todos los usuarios
            users_query = conn.execute(users.select().
                                       where(users.c.verify_ident==1).
                                       where(users.c.disabled==1)).fetchall()
            print("entra en el segundo if: ", users_query)
        if not users_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se han encontrado usuarios")

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
