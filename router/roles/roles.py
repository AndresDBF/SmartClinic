from fastapi import APIRouter, HTTPException, status, Form, Response, Depends
from config.db import engine
from model.roles.roles import roles
from model.user import users
from router.paciente.user import authenticate_user, create_token, oauth2_scheme, user
from schema.rules.rules import Role
from sqlalchemy import insert, select, update, delete, join
from typing import List, Dict
from sqlalchemy import insert, select, func
from jose import jwt, JWTError

routerol = APIRouter(tags=['Roles'], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

SECRET_KEY = "0d227dc4d6ac7f607f532c85f5d8770215f3aa12398645b3bb74f09f1ebcbd51"
ALGORITHM = "HS256"


@routerol.get("/admin/roles/user",  status_code=status.HTTP_200_OK)
async def get_rules():  
    with engine.connect() as conn:
        query = conn.execute(roles.select()).fetchall()
        if not query:
            roles_data = [
                {"role_id": 1, "role_name": "Admin"},
                {"role_id": 2, "role_name": "Patient"},
                {"role_id": 3, "role_name": "Doctor"},
            ]
            conn.execute(roles.insert(), roles_data)
            conn.commit()
            query = conn.execute(roles.select()).fetchall()

            return roles_data  # Devuelve los datos predeterminados en lugar de una lista vacía

        list_roles = [
            {
                "role_id": row[0],
                "role_name": row[1]
            }
            for row in query
        ]  # Convierte los resultados en una lista de diccionarios
        return list_roles

def verify_data(role: str):
    with engine.connect() as conn:
        #query_username = conn.execute(users.select().where(users.c.username == username)).first()
        query_roles = conn.execute(roles.select().where(roles.c.role_name == role)).first()
        print(query_roles)
        if query_roles:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail= f"el rol ya existe")
        """  if query_username is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="no se ha encontrado el usuario") """
        return True

@routerol.post("/admin/roles/create")
async def create_rule(role: str = Form(...)):
    role = role.title()
    with engine.connect() as conn:
        query = verify_data(role)
        if query:
           print(role)
           conn.execute(insert(roles).values(role_name=role))
           conn.commit()
    return Response(content="El rol ha sido creado", status_code=status.HTTP_201_CREATED)

@routerol.put("/admin/roles/update/{rol_id}", response_model=Role)
async def update_rule(rol_id: int, new_rol: str = Form(...)):
    print(type(new_rol))
    with engine.connect() as conn:
        query_existing_role = conn.execute(roles.select().where(roles.c.role_name == new_rol)).first()
        if query_existing_role:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El rol '{new_rol}' ya existe")
        
        conn.execute(roles.update().where(roles.c.role_id == rol_id).values(role_name=new_rol))
        conn.commit()
        # Obtener el registro actualizado
        #updated_role = conn.execute(roles.select().where(roles.c.role_id == rol_id)).first()          
        
    return Response(content="El rol se ha actualizado", status_code=status.HTTP_200_OK)


@routerol.delete("/admin/rules/delete/{rol_id}")
async def delete_rule(rol: str):
    with engine.connect() as conn:
        conn.execute(roles.delete().where(roles.c.role_id == rol))
        conn.commit()
        return Response(content="El rol se ha eliminado", status_code=status.HTTP_204_NO_CONTENT)

""" 
#route en desarrollo...
@rule.post("/", tags=["rules"])
async def verify_rules():
    with engine.connect() as conn:
        query = conn.execute(rules.select()).fetchall()
        print(query)
        if query is not None:
            return RedirectResponse(url="/api/user/login", status_code=status.HTTP_301_MOVED_PERMANENTLY)
        rule_user = conn.execute(insert(rules).values(1,"usuario"))
        conn.execute(rule_user)
        conn.commit()
        rule_user = conn.execute(insert(rules).values(1,"doctor"))
        conn.execute(rule_user)
        conn.commit()
    return RedirectResponse(url="/api/user/login", status_code=status.HTTP_201_CREATED)
"""