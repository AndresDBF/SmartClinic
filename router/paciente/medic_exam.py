import os
import hashlib

from fastapi import APIRouter, Request, HTTPException, status, Depends, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config.db import engine
from model.user import users
from model.images.files_medical_exam_doc import files_medical_exam_doc
from model.images.files_medical_exam_pat import files_medical_exam_pat
from model.inf_medic import inf_medic 
from model.medical_exam import medical_exam
from model.roles.user_roles import user_roles

from router.logout import get_current_user
from router.roles.user_roles import verify_rol


from jose import jwt, JWTError


userexam = APIRouter(tags=["Users"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})


@userexam.get("/api/user/myexam/")
async def list_user_exam(user_id: int, request: Request, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        exams = conn.execute(
            select(medical_exam.c.id,
                   medical_exam.c.description_exam,
                   medical_exam.c.done)
            .select_from(medical_exam)
            .where(medical_exam.c.user_id == user_id)
        ).fetchall()
    list_exams = [
        {
            "id": exam[0],
            "description_exam": exam[1],
            "done": exam[2]
        } 
        for exam in exams
    ]
    data_list = []
    for exam in list_exams:
        exam_id = exam["id"]
        full_data = exam
        with engine.connect() as conn:
            files = conn.execute(files_medical_exam_doc.select().where(files_medical_exam_doc.c.exam_id == exam_id)).first()
        if files.pdf_exam_original:
            if files.pdf_exam_original[-4:] == ".pdf":
                file_path_file = f"./img/medic/{files.pdf_exam}{files.pdf_exam_original[-4:]}"
                print(file_path_file)
                if not os.path.exists(file_path_file):
                    return {"error": "La imagen de perfil no existe"}

                prof_img = FileResponse(file_path_file)
                base_url = str(request.base_url)
                url_file = f"{base_url.rstrip('/')}/img/medic/{files.pdf_exam}{files.pdf_exam_original[-4:]}" 
                full_data["url_file"] = url_file
            else:
                file_path_file = f"./img/medic/{files.pdf_exam}{files.pdf_exam_original[-5:]}"
                print(file_path_file)
                if not os.path.exists(file_path_file):
                    return {"error": "La imagen de perfil no existe"}

                prof_img = FileResponse(file_path_file)
                base_url = str(request.base_url)
                url_file = f"{base_url.rstrip('/')}/img/medic/{files.pdf_exam}{files.pdf_exam_original[-5:]}" 
                full_data["url_file"] = url_file
        if files.image_exam_original:
            file_path_file = f"./img/medic/{files.image_exam}.png"
            print(file_path_file)
            if not os.path.exists(file_path_file):
                return {"error": "La imagen de perfil no existe"}

            prof_img = FileResponse(file_path_file)
            base_url = str(request.base_url)
            url_file = f"{base_url.rstrip('/')}/img/medic/{files.image_exam}.png" 
            full_data["url_photo"] = url_file
        data_list.append(full_data)
    return data_list

@userexam.post("/api/user/updateexam/", status_code=status.HTTP_201_CREATED)
async def update_exam(exam_id: int, request: Request, file: UploadFile = File(None), photo: UploadFile = File(None),  current_user: str = Depends(get_current_user)):
    if file is not None and photo is not None:
        if file.filename != '' and photo.filename != '':
            url_files = await insert_two_files_exam(exam_id, request, file, photo)
            return JSONResponse(content={
                "saved": True,
                "message": "examen cargado correctamente",
                "files": url_files
            }, status_code=status.HTTP_201_CREATED)
    if file is not None or photo is not None:
        if photo is None:
            if file.filename != '':
                url_files = await insert_file_exam(exam_id, request, file)
                return JSONResponse(content={
                    "saved": True,
                    "message": "examen cargado correctamente",
                    "files": url_files
            }, status_code=status.HTTP_201_CREATED)
        if file is None:        
            if photo.filename != '':
                url_files = await insert_two_files_exam(exam_id, request, photo)
                return JSONResponse(content={
                    "saved": True,
                    "message": "examen cargado correctamente",
                    "files": url_files
                }, status_code=status.HTTP_201_CREATED)
                         
                    
async def insert_two_files_exam(id_exam: int, request: Request, file: UploadFile, image: UploadFile):
    try:
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
                
        with engine.connect() as conn:
            print(file.filename)
            print(image.filename)
            conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                                pdf_exam_original=file.filename, 
                                                                image_exam_original=image.filename,
                                                                pdf_exam=pr_file,
                                                                image_exam=pr_photo))
            conn.commit()     
        file_path_photo = f"./img/medic/{pr_photo}"
        file_path_file = f"./img/medic/{pr_file}"
        path_file = FileResponse(file_path_file)  
        path_image = FileResponse(file_path_photo)  
        base_url = str(request.base_url)
        image_url = f"{base_url.rstrip('/')}/img/medic/{pr_photo}.png"          
        if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            file_url = f"{base_url.rstrip('/')}/img/medic/{pr_photo}.docx"    
        if file.content_type == "application/pdf":
            file_url = f"{base_url.rstrip('/')}/img/medic/{pr_photo}.pdf"    
            
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen ya existe")
    created_user = {"url_file": file_url,"url_photo": image_url}
    return created_user  

async def insert_file_exam(id_exam: int, request: Request, file: UploadFile):
    try:
        if file.content_type not in ["image/jpeg", "image/jpg", "image/png", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/pdf"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser una imagen JPEG, JPG o PNG o un archivo PDF o Word")
        content_file = await file.read()
        
        pr_file = hashlib.sha256(content_file).hexdigest()
        
        if file.content_type in ["image/jpeg", "image/jpg", "image/png"]: 
            with open(f"img/medic/{pr_file}.png", "wb") as file_file:
                file_file.write(content_file)
            with engine.connect() as conn:
                conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                                    image_exam_original=file.filename,
                                                                    image_exam=pr_file))
                conn.commit()   
        if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            with open(f"img/medic/{pr_file}.docx", "wb") as file_image:
                file_image.write(content_file)
            with engine.connect() as conn:
                conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                                    pdf_exam_original=file.filename,
                                                                    pdf_exam=pr_file))
                conn.commit()   
        if file.content_type == "application/pdf":
            with open(f"img/medic/{pr_file}.pdf", "wb") as file_image:
                file_image.write(content_file)
            with engine.connect() as conn:
                conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                                    pdf_exam_original=file.filename,
                                                                    pdf_exam=pr_file))
                conn.commit()   
 
        file_path_file = f"./img/medic/{pr_file}"
        path_file = FileResponse(file_path_file)   
        
        base_url = str(request.base_url)
        if file.content_type in ["image/jpeg", "image/jpg", "image/png"]: 
            file_url = f"{base_url.rstrip('/')}/img/medic/{pr_file}.png"          
        if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            file_url = f"{base_url.rstrip('/')}/img/medic/{pr_file}.docx"    
        if file.content_type == "application/pdf":
            file_url = f"{base_url.rstrip('/')}/img/medic/{pr_file}.pdf"    
            
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen ya existe")
    created_user = {"url_file": file_url}
    return created_user  
