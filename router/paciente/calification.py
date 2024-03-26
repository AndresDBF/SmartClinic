import os
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form, Response, Depends, Request
from fastapi.responses import JSONResponse, FileResponse

from config.db import engine

from model.user import users
from model.images.user_image_profile import user_image_profile
from model.experience_doctor import experience_doctor
from model.notification import notifications
from model.roles.user_roles import user_roles
from model.calification import calification_doc

from router.logout import get_current_user
from router.roles.roles import verify_rol_patient

from schema.calification import StarsDoctor, ExperienceDoctor

from datetime import datetime

from sqlalchemy import select, insert, func
#from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import IntegrityError

qualify = APIRouter(tags=["Users"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@qualify.get("/api/user/qualify-doc/")
async def calification_doctor(doc_id: int, request: Request, current_user = Depends(get_current_user)):
    verify_rol_patient(current_user)
    with engine.connect() as conn: 
        doctor = conn.execute(users.select().
                              join(user_roles, users.c.id==user_roles.c.user_id).
                              where(users.c.id==doc_id).
                              where(user_roles.c.role_id==3)).first()
        if doctor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no es doctor o no existe")
        exp_doc = conn.execute(experience_doctor.select().where(experience_doctor.c.user_id==doc_id)).first()
        if exp_doc is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El doctor no tiene registrada una especialidad")
        img_doctor = conn.execute(user_image_profile.select().where(user_image_profile.c.user_id==doc_id)).first() 
    if img_doctor is not None:
        file_path = f"./img/profile/{img_doctor.image_profile}.png"
        if not os.path.exists(file_path):
            return {"error": "El archivo no existe"}
            
        image = FileResponse(file_path)
            
        base_url = str(request.base_url)
        image_url = f"{base_url.rstrip('/')}/img/profile/{img_doctor.image_profile}.png"
        return {
            "id": doctor[0],
            "name": doctor[4],
            "last_name": doctor[5],
            "especiality_doctor": exp_doc[2],
            "url_img_profile": image_url
        }
    return {
        "id": doctor[0],
        "name": doctor[4],
        "last_name": doctor[5],
        "especiality_doctor": exp_doc[2],
        "url_img_profile": None
    }        
    
@qualify.post("/api/user/create-qualy/")
async def create_calification(doc_id: int, stars: StarsDoctor = Form(...), notes: str = Form(None), experiece: ExperienceDoctor = Form(...), current_user: str = Depends(get_current_user)):
    verify_rol_patient(current_user)
    with engine.connect() as conn: 
        doctor = conn.execute(users.select().where(users.c.id==doc_id)).first()
        if doctor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado ningun usuario")
        if notes:
            conn.execute(calification_doc.insert().values(user_id=doc_id, points=stars, notes= notes, experience= experiece)) 
            conn.commit()
            
        else:
            conn.execute(calification_doc.insert().values(user_id=doc_id, points=stars, notes= notes, experience= experiece)) 
            conn.commit()
    return JSONResponse(content={"saved": True, "message": "Calificacion Registrada"})