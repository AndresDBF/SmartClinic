import os
import hashlib

from fastapi import APIRouter, Request, HTTPException, status, Depends, UploadFile, File, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy import select, func, case, literal, or_
from sqlalchemy.exc import IntegrityError

from config.db import engine
from model.user import users
from model.images.files_medical_exam_doc import files_medical_exam_doc
from model.images.files_medical_exam_pat import files_medical_exam_pat
from model.inf_medic import inf_medic 
from model.medical_exam import medical_exam
from model.roles.user_roles import user_roles

from router.logout import get_current_user
from router.roles.roles import verify_rol_patient

from jose import jwt, JWTError

from typing import List, Optional

from datetime import datetime

userexam = APIRouter(tags=["Users"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@userexam.get("/api/user/my-exam-pend/")
async def list_user_exam(user_id: int, request: Request, page: Optional[int] = Query(1, ge=1), current_user: str = Depends(get_current_user)):
    verify_rol_patient(current_user)
    page_size = 25
    with engine.connect() as conn:
        exams = conn.execute(
        select(
            medical_exam.c.id,
            medical_exam.c.done,
            func.date_format(medical_exam.c.created_at, "%d/%m/%Y") 
        )
        .select_from(medical_exam)
        
        .where(medical_exam.c.user_id == user_id)
        .where(medical_exam.c.done == False)
       
        ).fetchall()
    total_history = len(exams)
    #manejo de paginacion
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    history_exam = exams[start_index:end_index]
    
    if not history_exam:
        return {"message": "No existen examenes pendientes"}, status.HTTP_404_NOT_FOUND
    
    history_exam = [
        {
            "id": exam[0],
            "done": exam[1],
            "datetime": exam[2],
            "files": []
        } 
        
        for exam in exams if exam[2] is not None or exam[3] is not None
    ]


    data_list = []
    for exam in history_exam:
        exam_id = exam["id"]   
        with engine.connect() as conn:
            files = conn.execute(files_medical_exam_doc.select().where(files_medical_exam_doc.c.exam_id == exam_id)).fetchall()
        files_list = []
        for file in files:
            if file.pdf_exam_original:
                print(file.pdf_exam,file.pdf_exam_original[-4:])
                print(file.image_exam)
                if file.pdf_exam_original[-4:] == ".pdf":
                    file_path_file = f"./img/medic/{file.pdf_exam}.pdf"
                    if not os.path.exists(file_path_file):
                        return {"error": "el documento del examen no existe"}
                    base_url = str(request.base_url)
                    url_file = f"{base_url.rstrip('/')}/img/patient/{file.pdf_exam}.pdf" 
                    name_file = file.pdf_exam_original[:-4]
                    files_list.append({"id_file": file.id,"file": name_file, "url_file": url_file, "completed": file.done})
                else:
                    file_path_file = f"./img/medic/{file.pdf_exam}.docx"
                    if not os.path.exists(file_path_file):
                        return {"error": "el documento del examen no existe"}
                    base_url = str(request.base_url)
                    url_file = f"{base_url.rstrip('/')}/img/patient/{file.pdf_exam}.docx" 
                    name_file = file.pdf_exam_original[:-5]
                    files_list.append({"id_file": file.id,"file": name_file, "url_file": url_file, "completed": file.done})
            if file.image_exam_original:
                print(file.image_exam_original)
                print(file.image_exam)
                file_path_file = f"./img/medic/{file.image_exam}.png"
                if not os.path.exists(file_path_file):
                    return {"error": "La imagen no existe"}
                base_url = str(request.base_url)
                url_file = f"{base_url.rstrip('/')}/img/patient/{file.image_exam}.png" 
                name_file = file.image_exam_original[:-4]
                files_list.append({"id_file": file.id,"file": name_file, "url_file": url_file, "completed": file.done})
        
        exam["files"] = files_list
        data_list.append(exam)
    total_pages = total_history // page_size
    if total_history % page_size != 0:
        total_pages += 1
    base_url = str(request.base_url)

    next_page = f"{base_url.rstrip('/')}/api/user/my-exam/?user_id={user_id}page={page + 1}" if page < total_pages else None
    previous_page = f"{base_url.rstrip('/')}/api/user/my-exam/?user_id={user_id}page={page - 1}" if page > 1 else None
    data_noti = {
        "links":{
        "next": next_page,
        "previous": previous_page
        },
        "data": data_list,
        "total": total_history,
    }
    return  data_noti

@userexam.get("/api/user/my-exam/")
async def list_user_exam(user_id: int, request: Request, page: Optional[int] = Query(1, ge=1), current_user: str = Depends(get_current_user)):
    verify_rol_patient(current_user)
    page_size = 25
    with engine.connect() as conn:
        exams = conn.execute(
        select(
            medical_exam.c.id,
            medical_exam.c.done,
            func.date_format(medical_exam.c.created_at, "%d/%m/%Y") 
        )
        .select_from(medical_exam)
        
        .where(medical_exam.c.user_id == user_id)
        .where(medical_exam.c.done == False)
       
        ).fetchall()
    total_history = len(exams)
    #manejo de paginacion
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    history_exam = exams[start_index:end_index]
    
    if not history_exam:
        return {"message": "No existen examenes"}, status.HTTP_404_NOT_FOUND
    
    history_exam = [
        {
            "id": exam[0],
            "done": exam[1],
            "datetime": exam[2],
            "files": []
        } 
        
        for exam in exams if exam[2] is not None or exam[3] is not None
    ]


    data_list = []
    for exam in history_exam:
        exam_id = exam["id"]   
        with engine.connect() as conn:
            files = conn.execute(files_medical_exam_pat.select().where(files_medical_exam_pat.c.exam_id == exam_id)).fetchall()
        files_list = []
        for file in files:
            if file.pdf_exam_original:
                print(file.pdf_exam,file.pdf_exam_original[-4:])
                print(file.image_exam)
                if file.pdf_exam_original[-4:] == ".pdf":
                    file_path_file = f"./img/medic/{file.pdf_exam}.pdf"
                    if not os.path.exists(file_path_file):
                        return {"error": "el documento del examen no existe"}
                    base_url = str(request.base_url)
                    url_file = f"{base_url.rstrip('/')}/img/patient/{file.pdf_exam}.pdf" 
                    name_file = file.pdf_exam_original[:-4]
                    files_list.append({"id_file": file.id,"file": name_file, "url_file": url_file})
                else:
                    file_path_file = f"./img/medic/{file.pdf_exam}.docx"
                    if not os.path.exists(file_path_file):
                        return {"error": "el documento del examen no existe"}
                    base_url = str(request.base_url)
                    url_file = f"{base_url.rstrip('/')}/img/patient/{file.pdf_exam}.docx" 
                    name_file = file.pdf_exam_original[:-5]
                    files_list.append({"id_file": file.id,"file": name_file, "url_file": url_file})
            if file.image_exam_original:
                print(file.image_exam_original)
                print(file.image_exam)
                file_path_file = f"./img/medic/{file.image_exam}.png"
                if not os.path.exists(file_path_file):
                    return {"error": "La imagen no existe"}
                base_url = str(request.base_url)
                url_file = f"{base_url.rstrip('/')}/img/patient/{file.image_exam}.png" 
                name_file = file.image_exam_original[:-4]
                files_list.append({"id_file": file.id,"file": name_file, "url_file": url_file})
        
        exam["files"] = files_list
        data_list.append(exam)
    total_pages = total_history // page_size
    if total_history % page_size != 0:
        total_pages += 1
    base_url = str(request.base_url)

    next_page = f"{base_url.rstrip('/')}/api/user/my-exam/?user_id={user_id}page={page + 1}" if page < total_pages else None
    previous_page = f"{base_url.rstrip('/')}/api/user/my-exam/?user_id={user_id}page={page - 1}" if page > 1 else None
    data_noti = {
        "links":{
        "next": next_page,
        "previous": previous_page
        },
        "data": data_list,
        "total": total_history,
    }
    return  data_noti

@userexam.post("/api/user/update-exam/", status_code=status.HTTP_201_CREATED)
async def update_exam(exam_id: int, id_file: int, request: Request, files: UploadFile = File(None), photos: UploadFile = File(None),  current_user: str = Depends(get_current_user)):
    verify_rol_patient(current_user)
    try:
        if files.filename != '':
            print("entra en el primer if ")
            if files.content_type not in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/pdf"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser un archivo Word o PDF, JPG, JPEG o PNG")
            url_file = await insert_file_exam(exam_id, request, files, id_file)
       
        if photos.filename != '':
            print("entra en el segundo if ")
            if photos.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser un archivo Word o PDF, JPG, JPEG o PNG")
            url_img = await insert_file_exam(exam_id, request, photos, id_file)
           
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Debe adjuntar almenos 1 archivo")            
        return JSONResponse(content={
                    "saved": True,
                    "message": "examen cargado correctamente",
                    "url_file": url_file,
                    "url_img": url_img
                    
                }, status_code=status.HTTP_201_CREATED)
    
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen ya existe") from e

async def insert_two_files_exam(id_exam: int, request: Request, file: UploadFile, images: UploadFile):
    try:
        if file.content_type not in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/pdf"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser un archivo Word o PDF")
        if images.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser una imagen JPEG, JPG o PNG")
        content_file = await file.read()
        content_image = await images.read()

        pr_file = hashlib.sha256(content_file).hexdigest()
        pr_photo = hashlib.sha256(content_image).hexdigest()

        with open(f"img/patient/{pr_photo}.png", "wb") as file_file:
            file_file.write(content_image)
        if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            with open(f"img/patient/{pr_file}.docx", "wb") as file_image:
                file_image.write(content_file)
        elif file.content_type == "application/pdf":
            with open(f"img/patient/{pr_file}.pdf", "wb") as file_image:
                file_image.write(content_file)

        with engine.connect() as conn:
                
            conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                                    pdf_exam_original=file.filename, 
                                                                    image_exam_original=images.filename,
                                                                    pdf_exam=pr_file,
                                                                    image_exam=pr_photo,
                                                                    created_at=func.now()))
            conn.commit()
        base_url = str(request.base_url)       
        file_url = f"{base_url.rstrip('/')}/img/patient/{pr_file}.pdf" if file.content_type == "application/pdf" else f"{base_url.rstrip('/')}/img/patient/{pr_file}.docx"
        base_url = str(request.base_url)
        image_url = f"{base_url.rstrip('/')}/img/patient/{pr_photo}.png"     

        with engine.connect() as conn:
            conn.execute(medical_exam.update().where(medical_exam.c.id==id_exam).values(done=True)) 
            conn.commit()

        return {"files": file_url, "images": image_url}
    
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen ya existe") from e

async def insert_file_exam(id_exam: int, request: Request, file: UploadFile, id_file: int):
    try:   
        content_file = await file.read()
        pr_file = hashlib.sha256(content_file).hexdigest()
        with engine.connect() as conn:
            if file.content_type in ["image/jpeg", "image/jpg", "image/png"]: 
                with open(f"img/patient/{pr_file}.png", "wb") as file_file:
                    file_file.write(content_file)
                    conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                                            image_exam_original=file.filename,
                                                                            image_exam=pr_file,
                                                                            created_at=func.now()))
                    conn.commit()   
                    conn.execute(files_medical_exam_doc.update().where(files_medical_exam_doc.c.id==id_file).values(done=True)) 
                    conn.commit()
            if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                with open(f"img/patient/{pr_file}.docx", "wb") as file_image:
                    file_image.write(content_file)
                    conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                                            pdf_exam_original=file.filename,
                                                                            pdf_exam=pr_file,
                                                                            created_at=func.now()))
                    conn.commit()   
                    conn.execute(files_medical_exam_doc.update().where(files_medical_exam_doc.c.id==id_file).values(done=True)) 
                    conn.commit()
            if file.content_type == "application/pdf":
                with open(f"img/patient/{pr_file}.pdf", "wb") as file_image:
                    file_image.write(content_file)
                    new_file = conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                                            pdf_exam_original=file.filename,
                                                                            pdf_exam=pr_file,
                                                                            created_at=func.now()))
                    conn.commit() 
                     
                    conn.execute(files_medical_exam_doc.update().where(files_medical_exam_doc.c.id==id_file).values(done=True)) 
                    conn.commit()
                    id_file = new_file.lastrowid
            ver_consult_completed = conn.execute(files_medical_exam_doc.select().where(files_medical_exam_doc.c.exam_id==id_exam)
                         .where(files_medical_exam_doc.c.done != True)).fetchall()
            if not ver_consult_completed:
                conn.execute(medical_exam.update().where(medical_exam.c.id==id_exam).values(done=True)) 
                conn.commit()

            base_url = str(request.base_url)
            if file.content_type in ["image/jpeg", "image/jpg", "image/png"]: 
                return {
                    "id_file": id_file,
                    "name": file.filename,
                    "url_file": f"{base_url.rstrip('/')}/img/patient/{pr_file}.png"
                }
                          
            elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return {
                    "id_file": id_file,
                    "name": file.filename,
                    "url_file": f"{base_url.rstrip('/')}/img/patient/{pr_file}.docx"
                }
                
            elif file.content_type == "application/pdf":
                return {
                    "id_file": id_file,
                    "name": file.filename,
                    "url_file": f"{base_url.rstrip('/')}/img/patient/{pr_file}.pdf"
                }
                    
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen ya existe") from e
            