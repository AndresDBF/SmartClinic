import os
from fastapi import APIRouter, Request, HTTPException, status, Depends, requests
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, case, literal

from config.db import engine
from model.user import users
from model.experience_doctor import experience_doctor
from model.images.user_image_profile import user_image_profile
from model.images.files_medical_exam_pat import files_medical_exam_pat
from model.person_antecedent import person_antecedent
from model.person_habit import personal_habit
from model.family_antecedent import family_antecedent
from model.inf_medic import inf_medic

from router.logout import get_current_user
from router.roles.user_roles import verify_rol



doctconsult = APIRouter(tags=["Doctor consult info"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})


@doctconsult.get("/doctor/info/consult/")
async def info_medic_consult(doc_id: int, patient_id: str, request: Request):
    with engine.connect() as conn:
        inf_med = conn.execute(inf_medic.select().where(inf_medic.c.doc_id==doc_id).where(inf_medic.c.user_id==patient_id)).first()
        doctor = conn.execute(select(users.c.name,
                                     users.c.last_name,
                                     experience_doctor.c.name_exper)
                              .select_from(users).where(users.c.id==doc_id)).first()
        img_profile = conn.execute(user_image_profile.select().where(user_image_profile.c.user_id==doc_id)).first()    
        
        files = conn.execute(files_medical_exam_pat.select().where(files_medical_exam_pat.c.user_id==doc_id)).fetchall()
        antecedent =  conn.execute(select( person_antecedent.c.hypertension,
                                            person_antecedent.c.diabetes,
                                            person_antecedent.c.asthma, 
                                            case(
                                                (person_antecedent.c.allergy_medicine_text.isnot(None), person_antecedent.c.allergy_medicine_text),
                                                else_=literal(None)).label("allergy_medicine_text"),
                                            case(
                                                (person_antecedent.c.allergy_foot_text.isnot(None), person_antecedent.c.allergy_foot_text),
                                                else_=literal(None)).label("allergy_foot_text"),
                                            case(
                                                (person_antecedent.c.other_condition_text.isnot(None), person_antecedent.c.other_condition_text),
                                                else_=literal(None)).label("other_condition_text"),
                                            case(
                                                (person_antecedent.c.operated_text.isnot(None), person_antecedent.c.operated_text),
                                                else_=literal(None)).label("operated_text"),
                                            case(
                                                (person_antecedent.c.take_medicine_text.isnot(None), person_antecedent.c.take_medicine_text),
                                                else_=literal(None)).label("take_medicine_text"),
                                            case(
                                                (person_antecedent.c.religion_text.isnot(None), person_antecedent.c.religion_text),
                                                else_=literal(None)).label("religion_text"),
                                            person_antecedent.c.job_occupation,
                                            case(
                                                (person_antecedent.c.disease_six_mounths_text.isnot(None), person_antecedent.c.disease_six_mounths_text),
                                                else_=literal(None)).label("disease_six_mounths_text"),
                                            person_antecedent.c.last_visit_medic,
                                            person_antecedent.c.visit_especiality,
                                            case(
                                                (family_antecedent.c.disease_mother_text.isnot(None), family_antecedent.c.disease_mother_text),
                                                else_=literal(None)).label("disease_mother_text"),
                                            case(
                                                (family_antecedent.c.disease_father_text.isnot(None), family_antecedent.c.disease_father_text),
                                                else_=literal(None)).label("disease_father_text"))
                                        .select_from(users.
                                                     join(person_antecedent, users.c.id == person_antecedent.c.user_id).
                                                     join(family_antecedent, users.c.id == family_antecedent.c.user_id))
                                        .where(users.c.id==patient_id)).first()
        antec_habit = conn.execute(select(personal_habit.c.consumed).select_from(personal_habit).where(personal_habit.c.user_id==patient_id)).fetchall()
    if files is not None:
        data_files = []
        for file in files:
            file_doc = file.pdf_exam_original[-4:]
            
            file_path_image = f"./img/patient/{file.image_exam}.png"
            if file_doc == ".pdf":
                file_path_doc = f"./img/patient/{file.pdf_exam}.pdf"
            else:
                file_path_doc = f"./img/patient/{file.pdf_exam}.pdf"
                
            if not os.path.exists(file_path):
                return {"error": "El archivo no existe"}
                
            image = FileResponse(file_path)
                
            base_url = str(request.base_url)
            image_url = f"{base_url.rstrip('/')}/img/profile/{img_profile.image_profile}.png"
    if img_profile is not None:
        file_path = f"./img/profile/{img_profile.image_profile}.png"
        if not os.path.exists(file_path):
            return {"error": "El archivo no existe"}
            
        image = FileResponse(file_path)
            
        base_url = str(request.base_url)
        image_url = f"{base_url.rstrip('/')}/img/profile/{img_profile.image_profile}.png"
        antecedent_patient = {
            "inf_medic": {
                "case": inf_med[6],
                "disease": inf_med[7],
                "imp_diag": inf_med[8],
                "medication": inf_med[9]
            },
            "person_antecedent": {
                "hypertension": antecedent[0],
                "diabetes": antecedent[1],
                "asthma": antecedent[2],
                "allergy_medicine_text": antecedent[3],
                "allergy_foot_text": antecedent[4],
                "other_condition_text": antecedent[5],
                "operated_text": antecedent[6],
                "take_medicine_text": antecedent[7],
                "religion_text": antecedent[8],
                "job_occupation": antecedent[9],
                "disease_six_mounths_text": antecedent[10],
                "last_visit_medic": antecedent[11],
                "visit_especiality": antecedent[12]
            },
            "personal_habit": list_habit,
            "family_antecedent": {
                "disease_mother_text": antecedent[13],
                "disease_father_text": antecedent[14]
            },
            "medic": {
                "name": doctor[0],
                "last_name": doctor[1],
                "name_exper": doctor[2]
            },
            "image_profile_doctor": None
        }
        return antecedent_patient

    list_habit = [
        {"consumed": habit.consumed}
        for habit in antec_habit
    ]

    antecedent_patient = {
        "inf_medic": {
            "case": inf_med[6],
            "disease": inf_med[7],
            "imp_diag": inf_med[8],
            "medication": inf_med[9]
        },
        "person_antecedent": {
            "hypertension": antecedent[0],
            "diabetes": antecedent[1],
            "asthma": antecedent[2],
            "allergy_medicine_text": antecedent[3],
            "allergy_foot_text": antecedent[4],
            "other_condition_text": antecedent[5],
            "operated_text": antecedent[6],
            "take_medicine_text": antecedent[7],
            "religion_text": antecedent[8],
            "job_occupation": antecedent[9],
            "disease_six_mounths_text": antecedent[10],
            "last_visit_medic": antecedent[11],
            "visit_especiality": antecedent[12]
        },
        "personal_habit": list_habit,
        "family_antecedent": {
            "disease_mother_text": antecedent[13],
            "disease_father_text": antecedent[14]
        },
        "medic": {
            "name": doctor[0],
            "last_name": doctor[1],
            "name_exper": doctor[2]
        },
        "image_profile_doctor": None
    }

    return antecedent_patient