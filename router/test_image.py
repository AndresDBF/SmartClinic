from fastapi import APIRouter, UploadFile, File, Form, status, Request
from fastapi.responses import FileResponse, JSONResponse
from os import getcwd, remove
from shutil import rmtree

router = APIRouter(tags=["testing file"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

""" 
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with open(getcwd() + "/" + file.filename, "wb") as myfile:
        content = await file.read()
        myfile.write(content)
        myfile.close()
    return "success"


@router.get("/file/{name_file}")
def get_file(name_file: str, request: Request):
    file_path = f"./img/profile/{name_file}"
    
    import os 
    if not os.path.exists(file_path):
        return {"error": "El archivo no existe"}
    
    image = FileResponse(file_path)
    
    base_url = str(request.base_url)
    image_url = f"{base_url.rstrip('/')}/img/profile/{name_file}"

    
    return {"id": 1, "image": image_url}
    
@router.get("/download/{name_file}")
def download_file(name_file: str):
    return FileResponse(getcwd() + "/" + name_file, media_type="application/octet-stream", filename=name_file)

@router.delete("/folder")
def delete_file(folder_name: str = Form(...)):
    rmtree(getcwd() + folder_name)
    return JSONResponse(content={
        "removed": True
    }, status_code=200) """