import string
import random
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form, Response
from fastapi.responses import JSONResponse
from config.db import engine
from model.user import users
from model.diagnostic import diagnostic
from schema.diagnostic import DiagnosticSchema, problem_patient
from datetime import date
from sqlalchemy import select, insert, func
from sqlalchemy.exc import IntegrityError


routediag = APIRouter(tags=["diagnostic"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@routediag.get("/api/diagnostic/{user_id}", status_code=status.HTTP_200_OK)
async def create_diagnostic(user_id: int):
    #para generar el id random 
    number_of_strings = 5
    length_of_string = 9
    
    id = "#" + "".join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(length_of_string)
    )
    id = id.upper() 
    #tomando los datos del usuario 
    try: 
        with engine.connect() as conn:
            user = conn.execute(users.select().where(users.c.id == user_id)).first()
        json_user = {
            "id_atent": id,
            "id_user": user[0],
            "name": user[4],
            "last_name": user[5],
            "birthdate": user[6],
            "gender": user[7]
        }
        return json_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

def verify_birthdate(userid: int, birthdate: date, gender: str):
    print(userid)
    print(birthdate)
    print(gender == "M" or gender == "F")
    if not gender == "M" or gender == "F":
        print("entra en gender")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El genero no es valido")
    with engine.connect() as conn:
        verify = conn.execute(users.select().where(users.c.id == userid).where(users.c.birthdate == birthdate)).first()
        print(verify)
        if not verify:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="las fechas de nacimiento no coinciden con los datos del usuario")
        return verify.id
        
@routediag.post("/api/diagnostic/new/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_diagnostic(userid: int, problem_patient: problem_patient, diag: DiagnosticSchema):
    full_name = diag.patient.title()
    print(diag)
    dict_diagnostic = diag.dict()
    print(dict_diagnostic)
    with engine.connect() as conn:
        if verify_birthdate(userid,diag.birthdate, diag.gender):
            last_id = conn.execute(select(func.max(diagnostic.c.id))).scalar()
            if last_id is not None:
                diag.id = last_id + 1
            else:
                diag.id = 1 
    
        conn.execute(diagnostic.insert().values(user_id=userid,
                                                probl_patient="diabetes",
                                                atent_id=dict_diagnostic["id_atent"],
                                                doctor_name=dict_diagnostic["doctor"]))
        conn.commit()
    created_diag = DiagnosticSchema(**dict_diagnostic)
    return created_diag 
        
@routediag.delete("/api/diagnostic/delete/{diag_id}")
async def delete_diagnostic(diag_id: int):
    with engine.connect() as conn:
        conn.execute(diagnostic.delete().where(diagnostic.c.id == diag_id))
        conn.commit()
    return Response(content="Se ha eliminado el diagnostico", status_code=status.HTTP_200_OK)