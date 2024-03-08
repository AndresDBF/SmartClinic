import os
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from config.db import engine
from model.user import users
from model.images.user_image_profile import user_image_profile

from router.logout import get_current_user
from router.roles.user_roles import verify_rol



# Obtener la ruta absoluta del directorio raíz del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

doctorhome = APIRouter(tags=["Doctor Home"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

# Definir la ruta absoluta de la carpeta de imágenes estáticas
img_directory = os.path.abspath(os.path.join(project_root, 'SmartClinic', 'img', 'profile'))

# Montar la carpeta de imágenes estáticas
doctorhome.mount("/img", StaticFiles(directory=img_directory), name="img")

@doctorhome.get("/doctor/home/{userid}")
async def user_home(userid: int, request: Request, current_user: str = Depends(get_current_user)):
    ver_user = await verify_rol(userid)
    print(ver_user)
    if ver_user["role_id"] == 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    
    with engine.connect() as conn:
        # Obtener el usuario
        user =  conn.execute(users.select().where(users.c.id == userid)).first()
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