import os
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from config.db import engine
from model.user import users
from model.images.user_image_profile import user_image_profile
from model.roles.user_roles import user_roles

from router.logout import get_current_user
from router.roles.user_roles import verify_rol


# Obtener la ruta absoluta del directorio raíz del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

patienthome = APIRouter(tags=["Patient Home"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

# Definir la ruta absoluta de la carpeta de imágenes estáticas
img_directory = os.path.abspath(os.path.join(project_root, 'SmartClinic', 'img', 'profile'))

# Montar la carpeta de imágenes estáticas
patienthome.mount("/img", StaticFiles(directory=img_directory), name="img")

@patienthome.get("/api/home/{userid}")
async def user_home(userid: int, request: Request, current_user: str = Depends(get_current_user)):    
    with engine.connect() as conn:
        user =  conn.execute(users.select().where(users.c.id == userid)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el usuario")
        
        ver_user = conn.execute(select(user_roles.c.role_id).select_from(user_roles).where(user_roles.c.user_id==userid)).first()
        
        if ver_user.role_id == 3:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
        # Obtener el usuario
        if ver_user.role_id == 2:
            
            veri_user =  conn.execute(users.select().where(users.c.id == userid).where(users.c.disabled==True).where(users.c.verify_ident==True)).first()
        
            if user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el usuario")
            if veri_user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se ha completado la verificacion del usuario")

        # Obtener la imagen del perfil del usuario
        image_row =  conn.execute(user_image_profile.select().where(user_image_profile.c.user_id == userid)).first()
        if image_row is not None:
            file_path = f"./img/profile/{image_row.image_profile}.png"
            if not os.path.exists(file_path):
                return {"error": "El archivo no existe"}
            
            image = FileResponse(file_path)
            
            base_url = str(request.base_url)
            image_url = f"{base_url.rstrip('/')}/img/profile/{image_row.image_profile}.png"
            
            return {"id": userid, "image": image_url}
        return {"id": userid, "image": None}

