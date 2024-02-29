import os
from fastapi import APIRouter, Request, HTTPException, status
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

@userhome.get("/home/")
async def user_home(request: Request, user_id: int):
    with engine.connect() as conn:
        # Obtener el usuario
        user = conn.execute(users.select().where(users.c.id == user_id)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el usuario")

        # Obtener la imagen del perfil del usuario
        image_row = conn.execute(user_image_profile.select().where(user_image_profile.c.image_profile == "prueba.png")).first()

        if image_row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado la imagen de perfil para este usuario")

        image_url = f"http://127.0.0.1:5000/img/prueba.png"  # Construye la URL completa para la imagen

        return {"image_url": image_url}
