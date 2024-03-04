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

from schema.antecedent_schema import Antecedent, AntecedentSchema, PersonalHobbieSchema, FamilyAntecedentSchema


routeantec = APIRouter(tags=["Users"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@routeantec.get("/api/newantecedent/")
async def new_antecedent(user_id: int):
    with engine.connect() as conn: 
        user = conn.execute(users.select().where(users.c.id==user_id)).first()
        if user is None: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el Usuario")
    return user[0]


from fastapi import HTTPException, status

@routeantec.post("/api/createantec/", response_model=AntecedentSchema)
async def create_antecedent(userid: int, data_per_antec: AntecedentSchema, data_per_hobb: PersonalHobbieSchema, data_fam_antec: FamilyAntecedentSchema):
    with engine.connect() as conn:
        new_data_per_antec = data_per_antec.dict()
        new_data_per_hobb = data_per_hobb.dict()
        new_data_fam_antec = data_fam_antec.dict()
        
        user = conn.execute(users.select().where(users.c.id==userid)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el usuario")
        
        # Insertar datos personales
        conn.execute(person_antecedent.insert().values(user_id=userid, **new_data_per_antec))
        conn.commit()
        
        # Insertar datos de hobbies personales
        conn.execute(person_hobbie.insert().values(user_id=userid, **new_data_per_hobb))
        conn.commit()
        
        # Insertar datos de antecedentes familiares
        conn.execute(family_antecedent.insert().values(user_id=userid, **new_data_fam_antec))
        conn.commit()
        
        # No es necesario utilizar zip para combinar los datos
        # Simplemente puedes retornar uno de los modelos
        return Antecedent(**new_data_per_antec)



    