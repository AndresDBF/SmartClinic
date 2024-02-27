from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi import Request
from config.db import engine
from model.images.user_image import user_image
from model.roles.user_roles import user_roles
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from typing import List

img = APIRouter(tags=['User_image'], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@img.post("/api/imageupload/{user_id}", status_code=status.HTTP_200_OK)
async def upload_image(user_id: int, request: Request, image_ident: UploadFile = File(...), image_self: UploadFile = File(...)):
    try:
        if image_ident.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo de identidad debe ser una imagen JPEG, JPG o PNG")
        if image_self.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La selfie debe ser una imagen JPEG, JPG o PNG")
        
        # Leer el contenido de los archivos
        content_ident = await image_ident.read()
        content_self = await image_self.read()

        # Guardar las imágenes en el servidor
        with open(f"img/identification/{image_ident.filename}", "wb") as file_ident:
            file_ident.write(content_ident)

        with open(f"img/selfie/{image_self.filename}", "wb") as file_self:
            file_self.write(content_self)   

        # Construir la URL de las imágenes
        #server_ip = request.client.host
        ident_url = f"http://localhost:8000/api/image/{user_id}/identification/{image_ident.filename}"
        selfie_url = f"http://localhost:8000/api/image/{user_id}/selfie/{image_self.filename}"


        # Guardar la información en la base de datos
        with engine.connect() as conn:
            query = user_image.insert().values(
                user_id=user_id,
                image_ident=image_ident.filename,
                image_self=image_self.filename
            )
            conn.execute(query)
            conn.commit()

        # Devolver una respuesta con la URL de las imágenes
        return JSONResponse(content={
            "saved": True,
            "message": "Se han guardado las imágenes correctamente",
            "identification_image_url": ident_url,
            "selfie_image_url": selfie_url
        }, status_code=status.HTTP_200_OK)
    
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image already exists")


    
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
    

 """

#--------------------NOTA ------------------------------------
#DEJAMOS ESTE CODIGO COMENTADO EN CASO DE QUE NECESITE SER USADO 






