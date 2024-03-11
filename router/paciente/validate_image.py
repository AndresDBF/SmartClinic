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

#importaciones para archivos .HEIC
import imghdr
#from pyheif import read
from PIL import Image
# Obtener la ruta absoluta del directorio raíz del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

imageuser = APIRouter(tags=["Verify Identification, Selfie"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

# Definir la ruta absoluta de la carpeta de imágenes estáticas
img_directory = os.path.abspath(os.path.join(project_root, 'SmartClinic', 'img', 'profile'))

# Montar la carpeta de imágenes estáticas
imageuser.mount("/img", StaticFiles(directory=img_directory), name="img")
'''
@imageuser.post("/api/imageupload/{user_id}", status_code=status.HTTP_200_OK)
async def upload_image(user_id: int, request: Request, image_ident: UploadFile = File(...), image_self: UploadFile = File(...),  current_user: str = Depends(get_current_user)):
    try:                
        if image_ident.content_type not in ["image/jpeg", "image/jpg", "image/png", "image/heic"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo de identidad debe ser una imagen JPEG, JPG o PNG")
        if image_self.content_type not in ["image/jpeg", "image/jpg", "image/png", "image/heic"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La selfie debe ser una imagen JPEG, JPG o PNG")
        
        # Leer el contenido de los archivos
        content_ident = await image_ident.read()
        content_self = await image_self.read()
        
        if image_ident.content_type == "image/heic":
            image_ident = convert_heic_to_png(content_ident, image_ident.filename)

            
        if image_self.content_type == "image/heic":
            image_self = convert_heic_to_png(content_self, image_self.filename)

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

# Función para convertir el archivo HEIC a PNG
def convert_heic_to_png(file_content, filename):
    heif_file = read(file_content)
    image = Image.frombytes(
        heif_file.mode, 
        heif_file.size, 
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    image.filename = filename  
    return image

# Verificar si el archivo es una imagen válida
def is_valid_image(content_type):
    return content_type in ["image/jpeg", "image/jpg", "image/png", "image/heic"]
    '''
#--------------------NOTA ------------------------------------
#DEJAMOS ESTE CODIGO COMENTADO EN CASO DE QUE NECESITE SER USADO 

@imageuser.post("/api/imageupload/{user_id}", status_code=status.HTTP_200_OK)
async def upload_image(user_id: int, request: Request, image_ident: UploadFile = File(..., description="imagen de identidad"), image_self: UploadFile = File(..., description="imagen de selfie"),  current_user: str = Depends(get_current_user)):
    with engine.connect() as conn: 
        veri_admin = conn.execute(select(user_roles.c.role_id).
                                  select_from(user_roles).where(user_roles.c.user_id==user_id)).first()
    if veri_admin[0] == 1:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="El administrador no debe verificar su identidad")
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

