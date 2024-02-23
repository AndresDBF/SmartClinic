from fastapi import APIRouter, HTTPException, status, Form, Response
from config.db import engine
from model.roles.roles import roles
from model.user import users
from model.roles.user_roles import user_roles
from schema.rules.rules import Role
from sqlalchemy import insert, select, update, delete, join,and_
from typing import List, Dict
from sqlalchemy import insert, select, func

routeuserrol = APIRouter(tags=['user_roles'], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})


@routeuserrol.get("/admin/userroles/user", tags=["user_roles"], status_code=status.HTTP_200_OK)
async def get_userroles():
    with engine.connect() as conn:
        
        query = conn.execute(
            select(
                users.c.id,
                roles.c.role_id,
                users.c.username,
                roles.c.role_name,
                users.c.name,
                users.c.last_name
            ).select_from(
                users.
                join(user_roles, users.c.id == user_roles.c.user_id).
                join(roles, user_roles.c.role_id == roles.c.role_id)
            )
        ).fetchall()
        print(query)        
        list_roles = [
            {
                "id": row[0],
                "role_id": row[1],
                "username": row[2],
                "role_name": row[3],
                "name": row[4],
                "last_name": row[5]
            }
            for row in query
        ]
        print(list_roles)
        if not list_roles:
            #Define los datos de los roles predeterminados
            return Response(content="No se han asignado roles a los usuarios", status_code=status.HTTP_204_NO_CONTENT)
        return list_roles

def verify_user_roles(role: str, username: str):
    with engine.connect() as conn:
        print(role)
        print(username)
        #query_username = conn.execute(users.select().where(users.c.username == username)).first()
        query_roles = conn.execute(roles.select().where(roles.c.role_name == role)).first()
        print(query_roles)
        query_username = conn.execute(users.select().where(users.c.username == username)).first()
        print(query_username)
        if query_roles is None: 
            if query_username is None and query_roles:
                raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No se ha encontrado el usuario")
            if query_username is None and query_roles is None:
                raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No se ha encontrado ningun dato")
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No se ha encontrado el rol")
        rol_user = conn.execute(user_roles.select().where(user_roles.c.role_id == query_roles)
                                .where(user_roles.c.user_id == query_username)).first()
        print(rol_user)
        if rol_user is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El usuario ya tiene asignado el rol de {role}")
        return {
            "user_id": query_username[0],
            "role_id": query_roles[0]
        }
        
@routeuserrol.post("/admin/userroles/create")
async def create_user_role(role: str = Form(...), username: str = Form(...)):
    role = role.title()
    with engine.connect() as conn:
        query = verify_user_roles(role, username)
        if query:
            print(query)
           
            conn.execute(user_roles.insert().values(query))
            conn.commit()
    return Response(content="El rol al usuario ha sido creado", status_code=status.HTTP_201_CREATED)

def get_data(rol: str, username: str):
    with engine.connect() as conn:
        query = conn.execute(
            select(
                users.c.id,
                roles.c.role_id,
            ).select_from(
                users.
                join(user_roles, users.c.id == user_roles.c.user_id).
                join(roles, user_roles.c.role_id == roles.c.role_id)
            ).where(user_roles.c.role_id == rol).where(user_roles.c.user_id == username)
        ).first()

        list_query = {
                "user_id": query[0],
                "role_id": query[1]
            }
        return list_query
            
@routeuserrol.put("/admin/userroles/create/{rol_id}/{user_id}")
async def update_user_role(roleid: int, userid: int, new_rol: str = Form(...), new_user_rol: str = Form(...)):
    new_rol = new_rol.title()
    with engine.connect() as conn:
       
        print(new_rol)
        print(new_user_rol)

        # Define las columnas que deseas seleccionar como instancias de objetos de columna
        user_id_column = users.c.id
        username_column = users.c.username
        role_id_column = roles.c.role_id
        role_name_column = roles.c.role_name
        user_role_user_id_column = user_roles.c.user_id
        user_role_role_id_column = user_roles.c.role_id

        # Realiza la consulta con las instancias de objetos de columna
        query = conn.execute(
            select([
                user_id_column, 
                username_column, 
                role_id_column, 
                role_name_column,  
                user_role_user_id_column, 
                user_role_role_id_column
            ]).select_from(
                join(users, user_roles, users.c.id == user_roles.c.user_id).
                join(roles, user_roles.c.role_id == roles.c.role_id)
            ).where(
                and_(roles.c.role_name == new_rol, users.c.username == new_user_rol)
            )
        ).fetchall()

        print(query)
        if query:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El usuario {new_user_rol} ya tiene asignado el rol de {new_rol}")
        
        user_data = get_data(roleid, userid)
        conn.execute(user_roles.update().where(user_roles.c.role_id == roleid).
                     where(user_roles.c.user_id == userid).values(user_data))
        conn.commit()
    return Response(content="Usuario actualizado correctamente", status_code= status.HTTP_200_OK)

















""" def verify_roles(role: str, username: str):
    role = role.title()
    with engine.connect() as conn:
        query_username = conn.execute(users.select().where(users.c.username == username))[0].first()
        query_roles = conn.execute(roles.select().where(roles.c.role_name == role))[0].first()
        rol_user = conn.execute(user_roles.select().where(user_roles.c.role_id == query_roles)
                                .where(user_roles.c.user_id == query_username)).first()
        if rol_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail= f"El usuario tiene asignado el rol {role}")
        return True
 """