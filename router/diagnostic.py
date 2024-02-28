import string
import random

from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form, Response
from fastapi.responses import JSONResponse

from config.db import engine

from model.user import users
from model.diagnostic import diagnostic
from model.patient_consult import patient_consult

from schema.diagnostic import DiagnosticSchema

from datetime import date
from sqlalchemy import select, insert, func
from sqlalchemy.exc import IntegrityError


routediag = APIRouter(tags=["Diagnostic"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@routediag.get("/doctor/diagnostic/{pat_consult_id}", status_code=status.HTTP_200_OK)
async def create_diagnostic(pat_consult_id: int):
    try: 
        #para generar el id random 
        number_of_strings = 5
        length_of_string = 9
        
        id = "#" + "".join(
                random.choice(string.ascii_letters + string.digits)
                for _ in range(length_of_string)
        )
        id = id.upper() 
        #tomando los datos del usuario 

        with engine.connect() as conn:
            user = conn.execute(users.select().
                                join(patient_consult, users.c.id == patient_consult.c.user_id).
                                where(patient_consult.c.id == pat_consult_id)).first()
            if user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado ningun dato")
        json_user = {
            "idpatconsult": pat_consult_id,
            "id_atent": id,
            "id_user": user[0],
            "name": user[4],
            "last_name": user[5],
            "birthdate": user[6],
            "gender": user[7]
        }
        return json_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def verify_gender(gender: date):
    if not gender == "M" or gender == "F":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El genero no es valido")
    return True
        
@routediag.post("/doctor/diagnostic/new/{patconsultid}", status_code=status.HTTP_201_CREATED)
async def create_diagnostic(patconsultid: int, diag: DiagnosticSchema):
    full_name = diag.patient.title()
    dict_diagnostic = diag.dict()
    with engine.connect() as conn:
        verify_patconsult = conn.execute(patient_consult.select().where(patient_consult.c.id == patconsultid)).first()
        if verify_patconsult is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el id de la consulta para el paciente")
        if verify_gender(diag.gender):
            last_id = conn.execute(select(func.max(diagnostic.c.id))).scalar()
            if last_id is not None:
                diag.id = last_id + 1
            else:
                diag.id = 1 
    
        conn.execute(diagnostic.insert().values(id=dict_diagnostic["id"],
                                                patconsult_id=patconsultid,
                                                probl_patient=dict_diagnostic["problem_patient"],
                                                atent_id=dict_diagnostic["id_atent"],
                                                doctor_name=dict_diagnostic["doctor"]))
        conn.commit()
    created_diag = DiagnosticSchema(**dict_diagnostic)
    return created_diag 
        
@routediag.delete("/doctor/diagnostic/delete/{diag_id}")
async def delete_diagnostic(diag_id: int):
    with engine.connect() as conn:
        verify_id = conn.execute(diagnostic.select().where(diagnostic.c.id == diag_id)).first()
        if verify_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el id del diagnostico")
        conn.execute(diagnostic.delete().where(diagnostic.c.id == diag_id))
        conn.commit()
    return Response(content="Se ha cancelado el diagnostico", status_code=status.HTTP_200_OK)