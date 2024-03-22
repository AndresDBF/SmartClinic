import os
import hashlib

from fastapi import APIRouter, Request, HTTPException, status, Depends, UploadFile, File
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
from router.roles.user_roles import verify_rol

from jose import jwt, JWTError

from typing import List

from datetime import datetime

userexam = APIRouter(tags=["Users"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})



@userexam.get("/api/user/my-exam_pend/")
async def list_user_exam(user_id: int, request: Request, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        exams = conn.execute(
        select(
            medical_exam.c.id,
            medical_exam.c.done,
            case(
                (files_medical_exam_doc.c.pdf_exam_original.isnot(None), files_medical_exam_doc.c.pdf_exam_original),
                else_=literal(None)).label("file_pdf"),
            case(
                (files_medical_exam_doc.c.image_exam_original.isnot(None), files_medical_exam_doc.c.image_exam_original),
                else_=literal(None)).label("file_image"),
            func.date_format(medical_exam.c.created_at, "%d/%m/%Y") 
        )
        .select_from(medical_exam)
        .join(files_medical_exam_doc, medical_exam.c.id == files_medical_exam_doc.c.exam_id)
        .where(medical_exam.c.user_id == user_id)
        .where(medical_exam.c.done == False)
        ).fetchall()

    list_exams = [
        {
            "id": exam[0],
            "done": exam[1],
            "datetime": exam[4],
            "files": []
        } 
        for exam in exams if exam[2] is not None or exam[3] is not None
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
                name_file = files.pdf_exam_original[:-4]
                full_data["name"] = name_file
                full_data["url_file"] = url_file

            else:
                file_path_file = f"./img/medic/{files.pdf_exam}{files.pdf_exam_original[-5:]}"
                print(file_path_file)
                if not os.path.exists(file_path_file):
                    return {"error": "La imagen de perfil no existe"}

                prof_img = FileResponse(file_path_file)
                base_url = str(request.base_url)
                url_file = f"{base_url.rstrip('/')}/img/medic/{files.pdf_exam}{files.pdf_exam_original[-5:]}" 
                name_file = files.pdf_exam_original[:-5]
                full_data["name"] = name_file
                full_data["url_file"] = url_file
               
        if files.image_exam_original:
            file_path_file = f"./img/medic/{files.image_exam}.png"
            print(file_path_file)
            if not os.path.exists(file_path_file):
                return {"error": "La imagen de perfil no existe"}

            prof_img = FileResponse(file_path_file)
            base_url = str(request.base_url)
            url_file = f"{base_url.rstrip('/')}/img/medic/{files.image_exam}.png" 
            name_file = files.pdf_exam_original[:-4]
            full_data["name"] = name_file
            full_data["url_file"] = url_file
        #REVISAR ESTE CODIGO PARA QUE MUESTRE BIEN ESTRUCTURADO EL JSON 
        data_list.append(full_data)
    return data_list

@userexam.get("/api/user/my-exam/")
async def list_user_exam(user_id: int, request: Request, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        exams = conn.execute(
        select(
            medical_exam.c.id,
            medical_exam.c.done,
            case(
                (files_medical_exam_pat.c.pdf_exam_original.isnot(None), files_medical_exam_pat.c.pdf_exam_original),
                else_=literal(None)).label("file_pdf"),
            case(
                (files_medical_exam_pat.c.image_exam_original.isnot(None), files_medical_exam_pat.c.image_exam_original),
                else_=literal(None)).label("file_image"),
            func.date_format(medical_exam.c.created_at, "%d/%m/%Y") 
        )
        .select_from(medical_exam)
        .join(files_medical_exam_pat, medical_exam.c.id == files_medical_exam_pat.c.exam_id)
        .where(medical_exam.c.user_id == user_id)
        .where(medical_exam.c.done == True)
        ).fetchall()

    list_exams = [
        {
            "id": exam[0],
            "done": exam[1],
            "datetime": exam[4]
        } 
        for exam in exams if exam[2] is not None or exam[3] is not None
    ]


    data_list = []
    for exam in list_exams:
        exam_id = exam["id"]
        full_data = exam
        data_list.append(full_data)
        with engine.connect() as conn:
            files = conn.execute(files_medical_exam_pat.select().where(files_medical_exam_pat.c.exam_id == exam_id)).first()
        if files.pdf_exam_original:
            if files.pdf_exam_original[-4:] == ".pdf":
                file_path_file = f"./img/patient/{files.pdf_exam}{files.pdf_exam_original[-4:]}"
                print(file_path_file)
                if not os.path.exists(file_path_file):
                    print("entra en el primer if ")
                    return {"error": "el documento del examen no existe"}

                prof_img = FileResponse(file_path_file)
                base_url = str(request.base_url)
                url_file = f"{base_url.rstrip('/')}/img/patient/{files.pdf_exam}{files.pdf_exam_original[-4:]}" 
                name_file = files.pdf_exam_original[:-4]
                data_list.append({"name": name_file, "url_file": url_file})
            else:
                file_path_file = f"./img/patient/{files.pdf_exam}{files.pdf_exam_original[-5:]}"
                print(file_path_file)
                if not os.path.exists(file_path_file):
                    print("entra en el segundo if ")
                    return {"error": "el documento del examen no existe"}

                prof_img = FileResponse(file_path_file)
                base_url = str(request.base_url)
                url_file = f"{base_url.rstrip('/')}/img/patient/{files.pdf_exam}{files.pdf_exam_original[-5:]}" 
                name_file = files.pdf_exam_original[:-5]
                data_list.append({"name": name_file, "url_file": url_file})
        if files.image_exam_original:
            file_path_file = f"./img/patient/{files.image_exam}.png"
            print(file_path_file)
            if not os.path.exists(file_path_file):
                return {"error": "La imagen de perfil no existe"}

            prof_img = FileResponse(file_path_file)
            base_url = str(request.base_url)
            url_file = f"{base_url.rstrip('/')}/img/patient/{files.image_exam}.png" 
            name_file = files.image_exam_original[:-4]
            data_list.append({"name": name_file, "url_file": url_file})
        
    return data_list

@userexam.post("/api/user/update-exam/", status_code=status.HTTP_201_CREATED)
async def update_exam(exam_id: int, request: Request, files: List[UploadFile] = File(None), photos: List[UploadFile] = File(None),  current_user: str = Depends(get_current_user)):
    try:
        print("este es el file: ",files)
        print("este es el photos: ",photos)
        data_files = []
        url_iamges = []
        # Procesar los archivos
        if files:
            for file in files:
                if file.filename != '':
                    print("entra en el primer if ")
                    if file.content_type not in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/pdf"]:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser un archivo Word o PDF, JPG, JPEG o PNG")
                    url_files = await insert_file_exam(exam_id, request, file)
                    data_files.append({"files": url_files})  
        # Procesar las fotos
        if photos:
            for photo in photos:
                if photo.filename != '':
                    print("entra en el segundo if ")
                    if photo.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser un archivo Word o PDF, JPG, JPEG o PNG")
                    url_files = await insert_file_exam(exam_id, request, photo)
                    url_iamges.append({"files": url_files})
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Debe adjuntar almenos 1 archivo")            
        return JSONResponse(content={
                    "saved": True,
                    "message": "examen cargado correctamente",
                    "url_files": data_files,
                    
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

async def insert_file_exam(id_exam: int, request: Request, file: UploadFile):
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
            if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                with open(f"img/patient/{pr_file}.docx", "wb") as file_image:
                    file_image.write(content_file)
                    conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                                            pdf_exam_original=file.filename,
                                                                            pdf_exam=pr_file,
                                                                            created_at=func.now()))
                    conn.commit()   
            if file.content_type == "application/pdf":
                with open(f"img/patient/{pr_file}.pdf", "wb") as file_image:
                    file_image.write(content_file)
                    conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                                            pdf_exam_original=file.filename,
                                                                            pdf_exam=pr_file,
                                                                            created_at=func.now()))
                    conn.commit()   
            conn.execute(medical_exam.update().where(medical_exam.c.id==id_exam).values(done=True)) 
            conn.commit()

            base_url = str(request.base_url)
            if file.content_type in ["image/jpeg", "image/jpg", "image/png"]: 
                return {
                    "name": file.filename,
                    "url_file": f"{base_url.rstrip('/')}/img/patient/{pr_file}.png"
                }
                          
            elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return {
                    "name": file.filename,
                    "url_file": f"{base_url.rstrip('/')}/img/patient/{pr_file}.docx"
                }
                
            elif file.content_type == "application/pdf":
                return {
                    "name": file.filename,
                    "url_file": f"{base_url.rstrip('/')}/img/patient/{pr_file}.pdf"
                }
                    
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen ya existe") from e
            

    

 

    with engine.connect() as conn:
        insert_exam = conn.execute(medical_exam.insert().values(user_id=patient_id, created_at=func.now()))
        conn.commit()
        id_ex = insert_exam.lastrowid
        data_exam = conn.execute(select(medical_exam.c.id,
                                        medical_exam.c.user_id,
                                        medical_exam.c.done,
                                        medical_exam.c.created_at).where(medical_exam.c.id==id_ex)).first()    
        print(data_exam)
    if file_docu or image:  
        if file_docu and image:  
            print("entra en el primer if")
            url_files = await insert_two_files_exam(id_ex, request, file_docu, image)
            print("este es el url_files: ",url_files )
            medic_exam = {
                "exam_id": data_exam[0],
                "user_id": data_exam[1],
                "datetime": data_exam[3],
                "done": data_exam[2]
            }
            medic_exam["files"] = url_files
        elif file_docu:  # Si solo hay documentos, inserta el archivo de documento
            print("entra en el segundo if")
            url_files = await insert_file_exam(id_ex, request, file_docu)
            medic_exam = {
                "exam_id": data_exam[0],
                "user_id": data_exam[1],
                "datetime": data_exam[3],
                "done": data_exam[2]
            }
            medic_exam["files"] = url_files
        elif image:  # Si solo hay imágenes, inserta la imagen
            print("entra en el tercer if")
            url_files = await insert_file_exam(id_ex, request, image)
            medic_exam = {
                "exam_id": data_exam[0],
                "user_id": data_exam[1],
                "datetime": data_exam[3],
                "done": data_exam[2],
            }
            medic_exam["files"] = url_files
        return medic_exam
    else:
        # Si no se proporcionan ni imágenes ni documentos, devuelve un mensaje de error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debes proporcionar al menos un archivo o imagen.")
     




























@userexam.get("/api/user/download-exam/")
async def download_file(filename: str):
    file_path = f"./img/patient/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El archivo no existe")
    return FileResponse(file_path)

""" @userexam.delete("/api/user/delete_exam/")
async def delete_file(filename: str):    
    file_path = f"./img/patient/{filename}"
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        raise HTTPException(status_code=404, detail="El archivo no existe")
    # También elimina el registro de la base de datos
    with engine.connect() as conn:
        ver_file = conn.execute(select(files_medical_exam_pat.c.pdf_exam_original, files_medical_exam_pat.c.pdf_exam).select_from(files_medical_exam_pat).
                                where(files_medical_exam_pat.c.pdf_exam_original.like(f'%{filename}%')))
        ver_file_img = conn.execute(select(files_medical_exam_pat.c.image_exam_original, files_medical_exam_pat.c.pdf_exam).select_from(files_medical_exam_pat)
                                    .where(files_medical_exam_pat.c.image_exam_original.like(f'%{filename}%')))
        
        if ver_file is not None:
            print("entra en el primer if")
            conn.execute(files_medical_exam_pat.update().where(files_medical_exam_pat.c.pdf_exam_original.like(f'%{filename}%')).
                         values(pdf_exam_original=None, pdf_exam=None))
            conn.commit()
        if ver_file_img is not None:
            conn.execute(files_medical_exam_pat.update().where(files_medical_exam_pat.c.image_exam_original.like(f'%{filename}%')).
                         values(image_exam_original=None, image_exam=None))
            conn.commit()
        if ver_file
    return JSONResponse(content={"removed": True, "message": "Archivo Eliminado correctamente"}, status_code=status.HTTP_204_NO_CONTENT) """
                          
"""               
async def insert_two_files_exam(id_exam: int, request: Request, file: UploadFile, image: UploadFile):

    if image.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser una imagen JPEG, JPG o PNG")
    if file.content_type not in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/pdf"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser un archivo word o pdf")
    print("pasa por los if de tipo de imagen")
    content_image = await image.read()
    content_file = await file.read()
    print("pasa los content")
    
        
    pr_photo = hashlib.sha256(content_image).hexdigest()
    pr_file = hashlib.sha256(content_file).hexdigest()
    print("pasa los encriptados")
    
    with open(f"img/patient/{pr_photo}.png", "wb") as file_file:
        file_file.write(content_image)
    
    if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        with open(f"img/patient/{pr_file}.docx", "wb") as file_image:
            file_image.write(content_file)
    if file.content_type == "application/pdf":
        with open(f"img/patient/{pr_file}.pdf", "wb") as file_image:
            file_image.write(content_file)
    print("guarda en el sistema de archivos")     
    with engine.connect() as conn:
        print(file.filename)
        print(image.filename)
        conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                            pdf_exam_original=file.filename, 
                                                            image_exam_original=image.filename,
                                                            pdf_exam=pr_file,
                                                            image_exam=pr_photo,
                                                            created_at=func.now()))
        print("ejecuta el insert")
        conn.commit()    
        conn.execute(medical_exam.update().where(medical_exam.c.id==id_exam).values(done=True)) 
        print("ejecuta el update")
        conn.commit()
    print("inserta en la base de datos")
    file_path_photo = f"./img/patient/{pr_photo}"
    file_path_file = f"./img/patient/{pr_file}"
    path_file = FileResponse(file_path_file)  
    path_image = FileResponse(file_path_photo)  
    base_url = str(request.base_url)
    image_url = f"{base_url.rstrip('/')}/img/patient/{pr_photo}.png"          
    if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        file_url = f"{base_url.rstrip('/')}/img/patient/{pr_file}.docx"    
    if file.content_type == "application/pdf":
        file_url = f"{base_url.rstrip('/')}/img/patient/{pr_file}.pdf"    
            
   
    created_user = {"url_file": file_url,"url_photo": image_url}
    return created_user
 """
""" async def insert_file_exam(id_exam: int, request: Request, files: list[UploadFile]):
    full_data = []
    for file in files:
        content_file = await file.read()
        
        pr_file = hashlib.sha256(content_file).hexdigest()
        with engine.connect() as conn:
            if file.content_type in ["image/jpeg", "image/jpg", "image/png"]: 
                with open(f"img/medic/{pr_file}.png", "wb") as file_file:
                    file_file.write(content_file)
                    conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                                        image_exam_original=file.filename,
                                                                        image_exam=pr_file,
                                                                        created_at=func.now()))
                    conn.commit()   
            if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                with open(f"img/patient/{pr_file}.docx", "wb") as file_image:
                    file_image.write(content_file)
                    conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                                        pdf_exam_original=file.filename,
                                                                        pdf_exam=pr_file,
                                                                        created_at=func.now()))
                    conn.commit()   
            if file.content_type == "application/pdf":
                with open(f"img/patient/{pr_file}.pdf", "wb") as file_image:
                    file_image.write(content_file)
                    conn.execute(files_medical_exam_pat.insert().values(exam_id=id_exam, 
                                                                        pdf_exam_original=file.filename,
                                                                        pdf_exam=pr_file,
                                                                        created_at=func.now()))
                    conn.commit()   
            conn.execute(medical_exam.update().where(medical_exam.c.id==id_exam).values(done=True)) 
            conn.commit()
        file_path_file = f"./img/patient/{pr_file}"
        path_file = FileResponse(file_path_file)   
        
        base_url = str(request.base_url)
        if file.content_type in ["image/jpeg", "image/jpg", "image/png"]: 
            file_url = f"{base_url.rstrip('/')}/img/patient/{pr_file}.png"          
        if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            file_url = f"{base_url.rstrip('/')}/img/patient/{pr_file}.docx"    
        if file.content_type == "application/pdf":
            file_url = f"{base_url.rstrip('/')}/img/patient/{pr_file}.pdf"    
                

        full_data.append({"url_file": file_url})
    return full_data
 """