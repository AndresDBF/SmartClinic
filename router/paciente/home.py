import os
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from config.db import engine
from model.user import users
from model.images.user_image_profile import user_image_profile

# Obtener la ruta absoluta del directorio raíz del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

userhome = APIRouter(tags=["userhome"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

# Definir la ruta absoluta de la carpeta de imágenes estáticas
img_directory = os.path.abspath(os.path.join(project_root, 'SmartClinic', 'img', 'profile'))

# Montar la carpeta de imágenes estáticas
userhome.mount("/img", StaticFiles(directory=img_directory), name="img")

@userhome.get("/home/{userid}")
async def user_home(userid: int, request: Request):
    with engine.connect() as conn:
        # Obtener el usuario
        user = conn.execute(users.select().where(users.c.id == userid)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el usuario")

        # Obtener la imagen del perfil del usuario
        image_row = conn.execute(user_image_profile.select().where(user_image_profile.c.user_id == userid)).first()

        file_path = f"./img/profile/{image_row.image_profile}"
    
        import os 
        if not os.path.exists(file_path):
            return {"error": "El archivo no existe"}
        
        image = FileResponse(file_path)
        
        base_url = str(request.base_url)
        image_url = f"{base_url.rstrip('/')}/img/profile/{image_row.image_profile}"

        
        return {"id": userid, "image": image_url}