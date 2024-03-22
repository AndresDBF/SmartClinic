from fastapi import APIRouter, HTTPException, status, Depends, Form
from fastapi.responses import  JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config.db import engine

from model.user import users
from model.roles.user_roles import user_roles
from model.images.user_image import user_image
from model.experience_doctor import experience_doctor
from model.usercontact import usercontact
from model.person_antecedent import person_antecedent
from model.person_habit import personal_habit
from model.family_antecedent import family_antecedent

from router.logout import get_current_user
from router.roles.user_roles import verify_rol

from schema.antecedent_schema import AntecedentSchema, PersonalHobbieSchema, FamilyAntecedentSchema, Antecedent


from sqlalchemy import select, insert, func

from typing import List

from datetime import datetime


routeantec = APIRouter(tags=["Antecedents"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@routeantec.get("/api/my-antecedents/")
async def user_antecedent(user_id: int,  current_user: str = Depends(get_current_user)):
    ver_user = await verify_rol(user_id)
    if ver_user["role_id"] == 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")


    with engine.connect() as conn:
        per_ant = conn.execute(
            person_antecedent.select()
            .where(person_antecedent.c.user_id == user_id)
            .order_by(person_antecedent.c.created_at.asc())
        ).fetchall()

        per_hob = conn.execute(
            personal_habit.select()
            .where(personal_habit.c.user_id == user_id)
            .order_by(personal_habit.c.created_at.asc())
        ).fetchall()

        ant_fam = conn.execute(
            family_antecedent.select()
            .where(family_antecedent.c.user_id == user_id)
            .order_by(family_antecedent.c.created_at.asc())
        ).fetchall()

        results1 = [
            {
                "hypertension": row[2],
                "diabetes": row[3],
                "asthma": row[4],
                "allergy_medicine_value": row[5],
                "allergy_medicine_text": row[6],
                "allergy_foot_value": row[7],
                "allergy_foot_text": row[8],
                "other_condition_value": row[9],
                "other_condition_text": row[10],
                "operated_value": row[11],
                "operated_text": row[12],
                "take_medicine_value": row[13],
                "take_medicine_text": row[14],
                "religion_value": row[15],
                "religion_text": row[16],
                "job_occupation": row[17],
                "disease_six_mounths_value": row[18],
                "disease_six_mounths_text": row[19],
                "last_visit_medic_text": row[20],
                "visit_especiality_text": row[21]
            }
            for row in per_ant
        ]
        results2 = [{"consumed": row[2]} for row in per_hob]
        results3 = [{"disease_mother": row[2],"disease_father": row[3]}for row in ant_fam]
        combined_result = zip(results1, results2)

        # Combina el resultado con la tercera lista de diccionarios
        list_antecedent = [
            {**result1, **result2, **result3}
            for (result1, result2), result3 in zip(combined_result, results3)
        ]
    return list_antecedent

@routeantec.get("/api/new-antecedent/")
async def new_antecedent(user_id: int,  current_user: str = Depends(get_current_user)):
    ver_user = await verify_rol(user_id)
    if ver_user["role_id"] == 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    with engine.connect() as conn: 
        user = conn.execute(users.select().where(users.c.id==user_id)).first()
        if user is None: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el Usuario")
    return user[0]

@routeantec.post("/api/create-antecedent/", response_model=Antecedent)
async def create_antecedent(userid: int, data_per_antec: AntecedentSchema, data_per_habit: List[PersonalHobbieSchema], data_fam_antec: FamilyAntecedentSchema,  current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        new_data_per_antec = data_per_antec.dict()
        new_data_fam_antec = data_fam_antec.dict()
        
        user = conn.execute(users.select().where(users.c.id==userid)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el usuario")
        new_data_per_antec['created_at'] = datetime.now()
        conn.execute(person_antecedent.insert().values(user_id=userid, **new_data_per_antec))
        conn.commit()
        
        for item in data_per_habit:
            
            consumed_str = item.consumed_text
            # Aquí se agrega el valor para created_at
            conn.execute(personal_habit.insert().values(user_id=userid,consumed=consumed_str, created_at=datetime.now()))
            conn.commit()
        
        conn.execute(family_antecedent.insert().values(user_id=userid, **new_data_fam_antec))
        conn.commit()

        return JSONResponse(content={"saved": True, "message": "Antecedente creado correctamente"}, status_code=status.HTTP_200_OK)


    