from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from config.db import engine
from typing import List

img = APIRouter(tags=['user_image'], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@img.post("/api/imageUpload", status_code=status.HTTP_201_CREATED)
async def upload_image(files: UploadFile = File(...)):
    print(files)
    try:
        for file in files:
            if file.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
                raise HTTPException(status_code=400, detail=f"El archivo '{file.filename}' debe ser una imagen JPEG o PNG")
            with open(f"uploads/{file.filename}", "wb") as f:
                content = await file.read()
                f.write(content)
        return JSONResponse(content={
            "saved": "Imágenes guardadas"
        }, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise JSONResponse(content={"error": "No se ha encontrado ninguna imagen"},
                           status_code=status.HTTP_404_NOT_FOUND)
        

#--------------------NOTA ------------------------------------
#DEJAMOS ESTE CODIGO COMENTADO EN CASO DE QUE NECESITE SER USADO 






