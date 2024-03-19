import hashlib
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form, Response, Depends, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config.db import engine

from model.tip_consult import tip_consult
from model.patient_consult import patient_consult
from model.user import users
from model.medical_exam import medical_exam
from model.images.files_medical_exam_doc import files_medical_exam_doc

from router.logout import get_current_user
from router.roles.user_roles import verify_rol

from schema.medic_exam import MedicExamSchema

from sqlalchemy import select, insert, func
from sqlalchemy.exc import IntegrityError

from typing import List

exam = APIRouter(tags=["Medical Exam"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@exam.get("/doctor/newmedicalex/", tags=["Video Call Doctor"])
async def new_medic_exam(user_id: int, current_user: str = Depends(get_current_user)):
    ver_user = await verify_rol(user_id)
    if ver_user["role_id"] == 2:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    with engine.connect() as conn: 
        user = conn.execute(
            select(users.c.id).
            select_from(users).
                where(users.c.id==user_id)).first()
        if user is None: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el Usuario")
    return user[0]

async def insert_two_files_exam(id_exam: int, request: Request, files: List[UploadFile], images: List[UploadFile]):
    try:
        urls = []
        for file, image in zip(files, images):
            if image.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser una imagen JPEG, JPG o PNG")
            if file.content_type not in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/pdf"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser un archivo Word o PDF")

            content_image = await image.read()
            content_file = await file.read()
            
            pr_photo = hashlib.sha256(content_image).hexdigest()
            pr_file = hashlib.sha256(content_file).hexdigest()
            
            with open(f"img/medic/{pr_photo}.png", "wb") as file_file:
                file_file.write(content_image)
            if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                with open(f"img/medic/{pr_file}.docx", "wb") as file_image:
                    file_image.write(content_file)
            elif file.content_type == "application/pdf":
                with open(f"img/medic/{pr_file}.pdf", "wb") as file_image:
                    file_image.write(content_file)
                
            with engine.connect() as conn:
                conn.execute(files_medical_exam_doc.insert().values(exam_id=id_exam, 
                                                                    pdf_exam_original=file.filename, 
                                                                    image_exam_original=image.filename,
                                                                    pdf_exam=pr_file,
                                                                    image_exam=pr_photo,
                                                                    created_at=func.now()))
                conn.commit()     

            base_url = str(request.base_url)
            image_url = f"{base_url.rstrip('/')}/img/medic/{pr_photo}.png"          
            file_url = f"{base_url.rstrip('/')}/img/medic/{pr_file}.pdf" if file.content_type == "application/pdf" else f"{base_url.rstrip('/')}/img/medic/{pr_file}.docx"
            
            urls.append({"url_file": file_url, "url_photo": image_url})

        return urls

    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen ya existe")

async def insert_file_exam(id_exam: int, request: Request, files: List[UploadFile]):
    try:
        urls = []
        for file in files:
            if file.content_type not in ["image/jpeg", "image/jpg", "image/png", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/pdf"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser una imagen JPEG, JPG o PNG o un archivo PDF o Word")
            content_file = await file.read()
            
            pr_file = hashlib.sha256(content_file).hexdigest()
            
            if file.content_type in ["image/jpeg", "image/jpg", "image/png"]: 
                with open(f"img/medic/{pr_file}.png", "wb") as file_file:
                    file_file.write(content_file)
                with engine.connect() as conn:
                    conn.execute(files_medical_exam_doc.insert().values(exam_id=id_exam, 
                                                                        image_exam_original=file.filename,
                                                                        image_exam=pr_file,
                                                                        created_at=func.now()))
                    conn.commit()   
            if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                with open(f"img/medic/{pr_file}.docx", "wb") as file_image:
                    file_image.write(content_file)
                with engine.connect() as conn:
                    conn.execute(files_medical_exam_doc.insert().values(exam_id=id_exam, 
                                                                        pdf_exam_original=file.filename,
                                                                        pdf_exam=pr_file,
                                                                        created_at=func.now()))
                    conn.commit()   
            if file.content_type == "application/pdf":
                with open(f"img/medic/{pr_file}.pdf", "wb") as file_image:
                    file_image.write(content_file)
                with engine.connect() as conn:
                    conn.execute(files_medical_exam_doc.insert().values(exam_id=id_exam, 
                                                                        pdf_exam_original=file.filename,
                                                                        pdf_exam=pr_file,
                                                                        created_at=func.now()))
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
            urls.append({"url_file": file_url})
        return urls
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen ya existe")

@exam.post("/doctor/createmedexam/", tags=["Video Call Doctor"])
async def create_medic_exam(patient_id: int, request: Request,  file_docu: List[UploadFile] = File(None), image: List[UploadFile] = File(None),  current_user: str = Depends(get_current_user)):
    print(file_docu)
    print(image)
    with engine.connect() as conn:
        insert_exam = conn.execute(medical_exam.insert().values(user_id=patient_id, created_at=func.now()))
        conn.commit()
        id_ex = insert_exam.lastrowid
        data_exam = conn.execute(medical_exam.select().where(medical_exam.c.id==id_ex)).first()    

    if file_docu or image:  
        if file_docu and image:  
            print("entra en el primer if")
            url_files = await insert_two_files_exam(id_ex, request, file_docu, image)
            print("este es el url_files: ",url_files )
            medic_exam = {
                "id": data_exam[0],
                "user_id": data_exam[1],
                "done": data_exam[2]
            }
            medic_exam["url_files"] = url_files
        elif file_docu:  # Si solo hay documentos, inserta el archivo de documento
            print("entra en el segundo if")
            url_files = await insert_file_exam(id_ex, request, file_docu)
            medic_exam = {
                "id": data_exam[0],
                "user_id": data_exam[1],
                "done": data_exam[2],
                "url_file": url_files
            }
            medic_exam["url_files"] = url_files
        elif image:  # Si solo hay imágenes, inserta la imagen
            print("entra en el tercer if")
            url_files = await insert_file_exam(id_ex, request, image)
            medic_exam = {
                "id": data_exam[0],
                "user_id": data_exam[1],
                "done": data_exam[2],
                "url_photo": url_files
            }
            medic_exam["url_files"] = url_files
        return medic_exam
    else:
        # Si no se proporcionan ni imágenes ni documentos, devuelve un mensaje de error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debes proporcionar al menos un archivo o imagen.")