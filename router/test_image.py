import hashlib
from fastapi import APIRouter, UploadFile, File, Form, status, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from os import getcwd, remove
from shutil import rmtree

router = APIRouter(tags=["testing file"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), image: UploadFile = File(...)):
    print(file.content_type)
    print(image.content_type)
    if image.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser una imagen JPEG, JPG o PNG")
    if file.content_type not in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/pdf"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser un archivo word o pdf")
    content_image = await image.read()
    content_file = await file.read()
        
    pr_photo = hashlib.sha256(content_image).hexdigest()
    pr_file = hashlib.sha256(content_file).hexdigest()
        
    with open(f"img/medic/{pr_photo}.png", "wb") as file_file:
        file_file.write(content_image)
    if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        with open(f"img/medic/{pr_file}.docx", "wb") as file_image:
            file_image.write(content_file)
    if file.content_type == "application/pdf":
        with open(f"img/medic/{pr_file}.pdf", "wb") as file_image:
            file_image.write(content_file)
    return "success"


@router.get("/file/{name_file}")
def get_file(name_file: str, request: Request):
    file_path = f"./img/medic/{name_file}"
    
    import os 
    if not os.path.exists(file_path):
        return {"error": "El archivo no existe"}
    
    image = FileResponse(file_path)
    
    base_url = str(request.base_url)
    image_url = f"{base_url.rstrip('/')}/img/medic/{name_file}"

    
    return {"id": 1, "image": image_url}
    
@router.get("/download/{name_file}")
def download_file(name_file: str):
    return FileResponse(getcwd() + "/" + name_file, media_type="application/octet-stream", filename=name_file)

@router.delete("/folder")
def delete_file(folder_name: str = Form(...)):
    rmtree(getcwd() + folder_name)
    return JSONResponse(content={
        "removed": True
    }, status_code=200) 