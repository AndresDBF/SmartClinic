import hashlib
import os
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from config.db import engine

from model.images.user_image import user_image
from model.roles.user_roles import user_roles

from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from typing import List

# Obtener la ruta absoluta del directorio raíz del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

imageuser = APIRouter(tags=["userhome"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

# Definir la ruta absoluta de la carpeta de imágenes estáticas
img_directory = os.path.abspath(os.path.join(project_root, 'SmartClinic', 'img', 'profile'))

# Montar la carpeta de imágenes estáticas
imageuser.mount("/img", StaticFiles(directory=img_directory), name="img")

@imageuser.post("/api/imageupload/{user_id}", status_code=status.HTTP_200_OK)
async def upload_image(user_id: int, request: Request, image_ident: UploadFile = File(...), image_self: UploadFile = File(...)):
    try:
        if image_ident.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo de identidad debe ser una imagen JPEG, JPG o PNG")
        if image_self.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La selfie debe ser una imagen JPEG, JPG o PNG")
        
        # Leer el contenido de los archivos
        content_ident = await image_ident.read()
        content_self = await image_self.read()


        # Generar un nombre único para las imágenes utilizando SHA256
        ident_hash = hashlib.sha256(content_ident).hexdigest()
        selfie_hash = hashlib.sha256(content_self).hexdigest()

        # Guardar las imágenes en el servidor con nombres encriptados
        with open(f"img/profile/{ident_hash}.png", "wb") as file_ident:
            file_ident.write(content_ident)

        with open(f"img/profile/{selfie_hash}.png", "wb") as file_self:
            file_self.write(content_self)   

        # Guardar la información en la base de datos
        with engine.connect() as conn:
            query = user_image.insert().values(
                user_id=user_id,
                image_ident_original=image_ident.filename,
                image_self_original=image_self.filename,
                image_ident=ident_hash,
                image_self=selfie_hash
            )
            conn.execute(query)
            conn.commit()
            image_row = conn.execute(user_image.select().where(user_image.c.user_id == user_id)).first()        
        
        file_path_ident = f"./img/profile/{image_row.image_ident}"
        file_path_self = f"./img/profile/{image_row.image_self}"
        

        image_ident = FileResponse(file_path_ident)
        image_self = FileResponse(file_path_self)
        
        base_url = str(request.base_url)
        image_url_ident = f"{base_url.rstrip('/')}/img/profile/{image_row.image_ident}.png"
        image_url_self = f"{base_url.rstrip('/')}/img/profile/{image_row.image_self}.png"        
        
        return JSONResponse(content={
            "saved": True,
            "message": "Se han guardado las imágenes correctamente",
            "identification_image_url": image_url_ident,
            "selfie_image_url": image_url_self
        }, status_code=status.HTTP_200_OK)
    
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image already exists")


'''    
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
        print(image_url)
        
        return {"id": userid, "image": image_url} """
""" 
img = APIRouter(tags=['user_image'], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@img.post("/api/imageupload", status_code=status.HTTP_201_CREATED)
async def upload_image(files: List[UploadFile] = File(...)):
    try:
        with engine.connect() as conn:
            for file in files:
                content = await file.read()
                try:
                    # Insert image info into user_image table
                    query = insert(user_image).values(image_ident=file.filename, image_self=content)
                    await session.execute(query)
                    await session.commit()
                except IntegrityError:
                    # Handle if the image already exists or other integrity errors
                    await session.rollback()
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image already exists")

        return {"saved": True}

    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
'''



#--------------------NOTA ------------------------------------
#DEJAMOS ESTE CODIGO COMENTADO EN CASO DE QUE NECESITE SER USADO 






