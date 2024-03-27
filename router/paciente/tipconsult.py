from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form, Response, Depends
from fastapi.responses import JSONResponse

from config.db import engine

from model.tip_consult import tip_consult
from model.patient_consult import patient_consult
from model.person_antecedent import person_antecedent

from router.logout import get_current_user
from router.roles.roles import verify_rol_patient

from datetime import datetime

from sqlalchemy import select, insert, func
from sqlalchemy.exc import IntegrityError

routetipco = APIRouter(tags=["Tip Consult"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@routetipco.get("/api/user/tip-consult-medic/")
async def get_tip_consult(user_id: int, current_user: str = Depends(get_current_user)):
    verify_rol_patient(current_user)
    with engine.connect() as conn:
        ver_ant = conn.execute(person_antecedent.select().where(person_antecedent.c.user_id == user_id)).first()
        print(ver_ant is None)
        print(ver_ant)
        if ver_ant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El antecedence del paciente no existe")
        ext_tip_consult = conn.execute(tip_consult.select()).fetchall()
        if ext_tip_consult:
            list_consult = [
                {
                    "id": row[0],
                    "tipconsult": row[1],
                    "user_id": user_id
                }
                for row in ext_tip_consult
            ]
            return JSONResponse(content=list_consult, status_code=status.HTTP_200_OK)
        
        new_list_consult = [
            
            {"id": 1, "tipconsult": "Consulta General"},
            {"id": 2, "tipconsult": "Salud Mental"},
            {"id": 3, "tipconsult": "Emergencia"}
        ]
        conn.execute(tip_consult.insert(), new_list_consult)
        conn.commit()
        query = conn.execute(tip_consult.select()).fetchall()
    list_consult = [
        {
            "id": row[0],
            "tipconsult": row[1],
            "user_id": user_id
        }
        for row in query
    ]
    return JSONResponse(content=list_consult, status_code=status.HTTP_200_OK)

@routetipco.post("/api/user/consult/{userid}/{consultid}/")
async def create_consult(userid: int, consultid: int, current_user: str = Depends(get_current_user)):
    verify_rol_patient(current_user)
    with engine.connect() as conn:
        last_pat_con_id = conn.execute(select(func.max(patient_consult.c.id))).scalar()
        if last_pat_con_id is not None:
            id_pc = last_pat_con_id + 1
        else:
            id_pc = 1 
        insert_cons = conn.execute(patient_consult.insert().values(id=id_pc, user_id=userid, tipconsult_id=consultid, consult_date=datetime.now()))
        conn.commit()
        last_query = conn.execute(patient_consult.select().where(patient_consult.c.id==id_pc)).first()
    return {
        "consult_id": last_query[0],
        "user_id": userid,
        "tipconsult_id": consultid,
        "consult_data": last_query[3]
    }
    
@routetipco.delete("/api/user/del-consult/{consult_id}/")
async def delete_pat_consult(consult_id: int, current_user: str = Depends(get_current_user)):
    verify_rol_patient(current_user)
    with engine.connect() as conn:
        query = conn.execute(patient_consult.delete().where(patient_consult.c.id == consult_id))       
        conn.commit()
    return Response(content="Se ha cancelado la consulta", status_code=status.HTTP_200_OK)
