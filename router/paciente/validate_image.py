import hashlib
import os
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from config.db import engine

from model.images.user_image import user_image
from model.roles.user_roles import user_roles

from router.logout import get_current_user

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
async def upload_image(user_id: int, request: Request, image_ident: UploadFile = File(...), image_self: UploadFile = File(...),  current_user: str = Depends(get_current_user)):
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



#--------------------NOTA ------------------------------------
#DEJAMOS ESTE CODIGO COMENTADO EN CASO DE QUE NECESITE SER USADO 


""" 



import hashlib
import imghdr
from pyheif import read
from PIL import Image
from fastapi import HTTPException, status
from sqlalchemy import insert

# Función para convertir el archivo HEIC a PNG
def convert_heic_to_png(file_content):
    heif_file = read(file_content)
    image = Image.frombytes(
        heif_file.mode, 
        heif_file.size, 
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    return image

# Verificar si el archivo es una imagen válida
def is_valid_image(content_type):
    return content_type in ["image/jpeg", "image/jpg", "image/png", "image/heic"]

# Lógica para manejar el envío de imágenes
if image is not None:
    if image.filename != '':
        try:
            content_type = image.content_type
            if not is_valid_image(content_type):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El archivo debe ser una imagen JPEG, JPG, PNG o HEIC"
                )
            
            content_image = await image.read()
            if content_type == "image/heic":
                image = convert_heic_to_png(content_image)
                file_extension = "png"
            else:
                image_extension = imghdr.what(None, content_image)
                file_extension = image_extension if image_extension else "png"
            
            image_hash = hashlib.sha256(content_image).hexdigest()
            image_path = f"img/profile/{image_hash}.{file_extension}"
            
            with open(image_path, "wb") as file:
                file.write(content_image)
            
            # Insertar la información en la base de datos
            await database.execute(
                insert(user_image_profile).values(
                    user_id=userid, 
                    image_profile_original=image.filename, 
                    image_profile=image_hash
                )
            )
            
            file_path_prof = f"./{image_path}"
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al procesar la imagen",
            ) from e
 """