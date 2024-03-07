import random
import string
import os 
from fastapi import APIRouter, HTTPException, status, Depends, Request, Form
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config.db import engine

from model.user import users
from model.roles.user_roles import user_roles
from model.images.user_image import user_image
from model.images.user_image_profile import user_image_profile
from model.experience_doctor import experience_doctor
from model.usercontact import usercontact
from model.person_antecedent import person_antecedent
from model.person_habit import personal_habit
from model.family_antecedent import family_antecedent
from model.inf_medic import inf_medic
from model.diagnostic import diagnostic

from sqlalchemy import select, insert, func
from sqlalchemy.sql import select

from router.paciente.home import get_current_user
from router.roles.user_roles import verify_rol

routeim = APIRouter(tags=["Video Call Doctor"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})


#optimizar las consultas de este endpoint
@routeim.get("/doctor/videocall/user/{user_id}")
async def get_info_user(user_id: int, request: Request):
    with engine.connect() as conn:
        user =  conn.execute(users.select().where(users.c.id == user_id)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el usuario")
            
        user_contact =  conn.execute(usercontact.select().where(usercontact.c.user_id==user_id)).first()
        
        number_of_strings = 5
        length_of_string = 9
        
        id = "#" + "".join(
                random.choice(string.ascii_letters + string.digits)
                for _ in range(length_of_string)
        )
        id = id.upper() 
        print(id)
        ant_per = conn.execute(
            select(
                person_antecedent.c.id
            )
            .select_from(person_antecedent)
            .where(person_antecedent.c.user_id==user_id)).first()
        if ant_per is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron antecedentes del paciente")
        hobb_per = conn.execute(personal_habit.select().where(personal_habit.c.user_id==user_id)).first()
        fam_per = conn.execute(family_antecedent.select().where(family_antecedent.c.user_id==user_id)).first()
        
        image_row = conn.execute(user_image.select().where(user_image.c.user_id == user_id)).first()
        if image_row is not None:
            file_path_ident = f"./img/profile/{image_row.image_ident}.png"
            file_path_self = f"./img/profile/{image_row.image_self}.png"
            if not os.path.exists(file_path_ident):
                return {"error": "El archivo no existe"}
            if not os.path.exists(file_path_self):
                return {"error": "El archivo no existe"}
            
            image = FileResponse(file_path_ident)
            image = FileResponse(file_path_self)
            
            base_url = str(request.base_url)
            image_url_ident = f"{base_url.rstrip('/')}/img/profile/{image_row.image_ident}.png"
            image_url_self = f"{base_url.rstrip('/')}/img/profile/{image_row.image_self}.png"
            inf_patient = {
                "iduser": user[0],
                "id_ant": ant_per[0],
                "id_hob": hobb_per[0],
                "id_fper": fam_per[0],
                "username": user[1],
                "id_atent": id,
                "email": user[2],
                "name": user[4],
                "last_name": user[5],
                "birthdate": user[6],
                "gender": user[7],
                "tipid": user[8],
                "identification": user[9],
                "phone": user_contact[2],
                "country": user_contact[3],
                "state": user_contact[4],
                "direction": user_contact[5],
                "image_ident": image_url_ident,
                "image_self": image_url_self
            }
            return inf_patient
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron archivos de identidad del paciente")

#optimizar las consultas de este endpoint      
@routeim.get("/doctor/infomedic/")
async def get_inf_medic_patient(user_id: int, id_ant: int, id_hob: int, id_fper: int, id_atent= str):
    with engine.connect() as conn:
        per_ant = conn.execute(
            select(
                person_antecedent.c.hypertension,
                person_antecedent.c.diabetes,
                person_antecedent.c.asthma, 
                person_antecedent.c.allergy_medicine,
                person_antecedent.c.allergy_foot,
                person_antecedent.c.other_condition,
                person_antecedent.c.operated,
                person_antecedent.c.take_medicine,
                person_antecedent.c.religion,
                person_antecedent.c.job_occupation,
                person_antecedent.c.disease_six_mounths,
                person_antecedent.c.last_visit_medic,
                person_antecedent.c.visit_especiality,
                person_antecedent.c.created_at,
            )
            .select_from(person_antecedent)
            .where(person_antecedent.c.id == id_ant)
            .order_by(person_antecedent.c.created_at.asc())
        ).first()

        if per_ant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se han encontrado antecedentes del usuario")
        per_hob = conn.execute(
            personal_habit.select()
            .where(personal_habit.c.id == id_hob)
            .order_by(personal_habit.c.created_at.asc())
        ).first()

        ant_fam = conn.execute(
            family_antecedent.select()
            .where(family_antecedent.c.id == id_fper)
            .order_by(family_antecedent.c.created_at.asc())
        ).first()
        result = {
                "id_atent": id_atent,
                "person_antedent":{
                    "hypertension": per_ant[0],
                    "diabetes": per_ant[1],
                    "asthma": per_ant[2],
                    "allergy_medicine": per_ant[3],
                    "allergy_foot": per_ant[4],
                    "other_condition": per_ant[5],
                    "operated": per_ant[6],
                    "take_medicine": per_ant[7],
                    "religion": per_ant[8],
                    "job_occupation": per_ant[9],
                    "disease_six_mounths": per_ant[10],
                    "last_visit_medic": per_ant[11],
                    "visit_especiality:": per_ant[12]
                },
                "personal_habit":{
                    "consumed": per_hob[2]
                },
                "anteceden_fam":{
                    "disease_mother": ant_fam[2],
                    "disease_father": ant_fam[3]
                }
        }
    return result

#modificar la optimizacion de este endpoint
@routeim.post("/doctor/infomedic/create/")
async def create_inf_medic(userid: int, id_exam: int, docid: int, id_ant: int, idatent: str, infcase: str = Form(...), disease_act: str = Form(...), impre_diag: str = Form(...), medication_ind: str = Form(...)):
    print(idatent)
    with engine.connect() as conn:
        conn.execute(inf_medic.insert().values(doc_id=docid,
                                               user_id=userid,
                                               ante_id=id_ant,
                                               exam_id=id_exam,
                                               atent_id=idatent,
                                               case= infcase,
                                               disease=disease_act,
                                               imp_diag=impre_diag,
                                               medication=medication_ind))
        conn.commit()
    return JSONResponse(content={
        "saved": True,
        "message": "Se ha creado el informe medico"
    }, status_code=status.HTTP_201_CREATED)
        
@routeim.delete("/doctor/infmedic/delete/{diag_id}")
async def delete_diagnostic(diag_id: int):
    with engine.connect() as conn:
        conn.execute(diagnostic.delete().where(diagnostic.c.id == diag_id))
        conn.commit()
    return Response(content="Se ha eliminado el diagnostico", status_code=status.HTTP_200_OK)