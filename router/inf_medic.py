from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form, Response

from config.db import engine

from model.diagnostic import diagnostic
from model.user import users

from schema.inf_medic import infMedicSchema

from sqlalchemy import select, insert, func
from sqlalchemy.exc import IntegrityError

routeim = APIRouter(tags=["medical information"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@routeim.get("/doctor/infm/{id_diag}")
async def get_diag_of_infm(id_diag: int):
    with engine.connect() as conn:
        query_diagnostic = conn.execute(diagnostic.select().where(diagnostic.c.id == id_diag)).first() 
        if query_diagnostic  is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado ningun diagnostico")    
        return {
                "id_diag": query_diagnostic[0],
                "patconsult_id": query_diagnostic[1],
                "probl_patient": query_diagnostic[2],
                "atent_id": query_diagnostic[3],
                "doctor_name": query_diagnostic[4]
            }

@routeim.post("/doctor/newinfm/")
async def create_new_infm():
    return "prueba"



@routeim.delete("/doctor/infmedic/delete/{diag_id}")
async def delete_diagnostic(diag_id: int):
    with engine.connect() as conn:
        conn.execute(diagnostic.delete().where(diagnostic.c.id == diag_id))
        conn.commit()
    return Response(content="Se ha eliminado el diagnostico", status_code=status.HTTP_200_OK)