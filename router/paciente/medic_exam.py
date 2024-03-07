import os
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select

from config.db import engine
from model.user import users
from model.images.files_medical_exam_doc import files_medical_exam_doc
from model.images.files_medical_exam_pat import files_medical_exam_pat
from model.inf_medic import inf_medic 
from model.medical_exam import medical_exam
from model.roles.user_roles import user_roles

from router.paciente.user import SECRET_KEY, ALGORITHM
from router.roles.user_roles import verify_rol

from jose import jwt, JWTError



userexam = APIRouter(tags=["Users"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@userexam.get("/api/user/myexam/")
async def list_user_exam(user_id: int):
    with engine.connect() as conn:
        exams = conn.execute(
                select(medical_exam.c.id,
                        medical_exam.c.description_exam,
                        medical_exam.c.done).select_from(medical_exam).
                join(users, medical_exam.c.user_id==users.c.id).where(users.c.id == user_id)).fetchall()
        exams_id = [rowex[0] for rowex in exams]
        
        image_row = conn.execute(files_medical_exam_doc.select().where(files_medical_exam_doc.c.user_id.in_(exams_id))).fetchall()

    list_exams = [
        {
            "id": exam[0],
            "description_exam": exam[1],
            "done": exam[2]
        } 
        for exam in exams
    ]
    full_data_exams = []
    for exam in list_exams:
        exam_id = exam["id"]
        image_row = conn.execute(files_medical_exam_doc.select().where(files_medical_exam_doc.c.user_id == user_id)).first()  # Ordenar por ID de imagen descendente
    pass


""" 
        # Combinar datos de usuario y contacto
        data_list = []
        for userdata in list_user:
            user_id = userdata["id"]
            user_contact_data = next((usercdata for usercdata in list_user_contact if usercdata["user_id"] == user_id), None)
            if user_contact_data:
                full_user_data = {**userdata, **user_contact_data}
            else:
                full_user_data = userdata
            # Obtener la imagen del perfil del usuario
            image_row = conn.execute(user_image_profile.select().where(user_image_profile.c.user_id == user_id).order_by(user_image_profile.c.id.desc())  # Ordenar por ID de imagen descendente
            ).first()
            
            if image_row:
                file_path_prof = f"./img/profile/{image_row.image_profile}.png"
                if not os.path.exists(file_path_prof):
                    return {"error": "La imagen de perfil no existe"}

                prof_img = FileResponse(file_path_prof)
                base_url = str(request.base_url)
                image_url_prof = f"{base_url.rstrip('/')}/img/profile/{image_row.image_profile}.png"
                full_user_data["url_prof_img"] = image_url_prof
            else:
                full_user_data["url_prof_img"] = None
            data_list.append(full_user_data) """