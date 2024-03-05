from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import  JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config.db import engine

from model.user import users
from model.roles.user_roles import user_roles
from model.images.user_image import user_image
from model.experience_doctor import experience_doctor
from model.usercontact import usercontact
from model.person_antecedent import person_antecedent
from model.person_hobbie import person_hobbie
from model.family_antecedent import family_antecedent

from sqlalchemy import select, insert, func

from router.paciente.home import get_current_user
from router.roles.user_roles import verify_rol

from schema.antecedent_schema import Antecedent, AntecedentSchema, PersonalHobbieSchema, FamilyAntecedentSchema


routeantec = APIRouter(tags=["Users"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@routeantec.get("/api/myantecedents/")
async def user_antecedent(user_id: int):
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
            person_hobbie.select()
            .where(person_hobbie.c.user_id == user_id)
            .order_by(person_hobbie.c.created_at.asc())
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
                "allergy_medicine": row[5],
                "allergy_foot": row[6],
                "other_condition": row[7],
                "operated": row[8],
                "take_medicine": row[9],
                "religion": row[10],
                "job_occupation": row[11],
                "disease_six_mounths": row[12],
                "last_visit_medic": row[13],
                "visit_especiality": row[14]
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

@routeantec.get("/api/newantecedent/")
async def new_antecedent(user_id: int):
    ver_user = await verify_rol(user_id)
    if ver_user["role_id"] == 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    with engine.connect() as conn: 
        user = conn.execute(users.select().where(users.c.id==user_id)).first()
        if user is None: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el Usuario")
    return user[0]


from fastapi import HTTPException, status

@routeantec.post("/api/createantec/", response_model=AntecedentSchema)
async def create_antecedent(userid: int, data_per_antec: AntecedentSchema, data_per_hobb: PersonalHobbieSchema, data_fam_antec: FamilyAntecedentSchema):
    ver_user = await verify_rol(userid)
    if ver_user["role_id"] == 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    with engine.connect() as conn:
        new_data_per_antec = data_per_antec.dict()
        new_data_per_hobb = data_per_hobb.dict()
        new_data_fam_antec = data_fam_antec.dict()
        
        user = conn.execute(users.select().where(users.c.id==userid)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el usuario")

        conn.execute(person_antecedent.insert().values(user_id=userid, **new_data_per_antec))
        conn.commit()

        conn.execute(person_hobbie.insert().values(user_id=userid, **new_data_per_hobb))
        conn.commit()

        conn.execute(family_antecedent.insert().values(user_id=userid, **new_data_fam_antec))
        conn.commit()
        

        return AntecedentSchema(**new_data_per_antec)



    