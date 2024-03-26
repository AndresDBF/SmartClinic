import os
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, func, or_, and_, between

from config.db import engine
from model.user import users
from model.images.user_image_profile import user_image_profile
from model.medical_exam import medical_exam
from model.inf_medic import inf_medic

from router.logout import get_current_user
from router.roles.roles import verify_rol_doctor

from typing import Optional

from sqlalchemy import func
from datetime import datetime, timedelta


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
doctorhome = APIRouter(tags=["Doctor Home"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})
img_directory = os.path.abspath(os.path.join(project_root, 'SmartClinic', 'img', 'profile'))
doctorhome.mount("/img", StaticFiles(directory=img_directory), name="img")

#created_at, "%d/%m/%Y"
@doctorhome.get("/doctor/home-case/{doc_id}/")
async def user_home(doc_id: int, request: Request, search_case: Optional[str] = None, search_type: Optional[str] = None, current_user: str = Depends(get_current_user)):
    verify_rol_doctor(current_user)
    with engine.connect() as conn:
        user =  conn.execute(users.select().where(users.c.id == doc_id)).first()
        veri_user =  conn.execute(users.select().where(users.c.id == doc_id).where(users.c.disabled==True).where(users.c.verify_ident==True)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el usuario")
        if veri_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se ha completado la verificacion del usuario")
        if search_case:
            name_parts = search_case.split()
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            if search_type == "week":
                print("entra al primer if")
                today = datetime.now().date()
                monday = today - timedelta(days=today.weekday())
                monday_midnight = datetime.combine(monday, datetime.min.time())
                
                case_pat = conn.execute(select(inf_medic.c.id,
                                            inf_medic.c.doc_id,
                                            inf_medic.c.user_id,
                                            users.c.name,
                                            users.c.last_name,
                                            inf_medic.c.finished,
                                            func.date_format(inf_medic.c.created_at, "%d/%m"))
                                    .select_from(inf_medic)
                                    .join(users, inf_medic.c.user_id == users.c.id).where(
                                        or_(
                                            and_(
                                                users.c.name.like(f'%{first_name}%'),
                                                users.c.last_name.like(f'%{last_name}%')
                                            ),
                                            and_(
                                                users.c.last_name.like(f'%{last_name}%'),
                                                users.c.name.like(f'%{first_name}%')
                                            ),
                                            users.c.name.like(f'%{search_case}%'),
                                            users.c.last_name.like(f'%{search_case}%')
                                    ))
                                    .where(inf_medic.c.doc_id == doc_id)
                                    .where(inf_medic.c.created_at >= monday_midnight)
                                    .where(inf_medic.c.created_at <= datetime.now())).fetchall()
               
            elif search_type == "day":
                print("entra al segundo if")
                one_day_ago = datetime.combine(datetime.now() - timedelta(days=1),datetime.min.time())
              
                case_pat = conn.execute(select(inf_medic.c.id,
                                            inf_medic.c.doc_id,
                                            inf_medic.c.user_id,
                                            users.c.name,
                                            users.c.last_name,
                                            inf_medic.c.finished,
                                            func.date_format(inf_medic.c.created_at, "%d/%m"))
                                    .select_from(inf_medic)
                                    .join(users, inf_medic.c.user_id == users.c.id).where(
                                        or_(
                                            and_(
                                                users.c.name.like(f'%{first_name}%'),
                                                users.c.last_name.like(f'%{last_name}%')
                                            ),
                                            and_(
                                                users.c.last_name.like(f'%{last_name}%'),
                                                users.c.name.like(f'%{first_name}%')
                                            ),
                                            users.c.name.like(f'%{search_case}%'),
                                            users.c.last_name.like(f'%{search_case}%')
                                    ))
                                    .where(inf_medic.c.doc_id == userid)
                                    .where(inf_medic.c.created_at >= one_day_ago)).fetchall()
              
            elif search_type == "month":
                print("entra al tercer if")
                first_day_of_month = datetime.now().replace(day=1)
                first_day_of_month_midnight = datetime.combine(first_day_of_month, datetime.min.time())
               
                case_pat = conn.execute(select(inf_medic.c.id,
                                            inf_medic.c.doc_id,
                                            inf_medic.c.user_id,
                                            users.c.name,
                                            users.c.last_name,
                                            inf_medic.c.finished,
                                            func.date_format(inf_medic.c.created_at, "%d/%m"))
                                    .select_from(inf_medic)
                                    .join(users, inf_medic.c.user_id == users.c.id).where(
                                        or_(
                                            and_(
                                                users.c.name.like(f'%{first_name}%'),
                                                users.c.last_name.like(f'%{last_name}%')
                                            ),
                                            and_(
                                                users.c.last_name.like(f'%{last_name}%'),
                                                users.c.name.like(f'%{first_name}%')
                                            ),
                                            users.c.name.like(f'%{search_case}%'),
                                            users.c.last_name.like(f'%{search_case}%')
                                    ))
                                    .where(inf_medic.c.doc_id == userid)
                                    .where(inf_medic.c.created_at >= first_day_of_month_midnight)
                                    .where(inf_medic.c.created_at <= datetime.now())).fetchall()
              
            else:
                print("entra al cuarto if")
                case_pat = conn.execute(select(inf_medic.c.id,
                                            inf_medic.c.doc_id,
                                            inf_medic.c.user_id,
                                            users.c.name,
                                            users.c.last_name,
                                            inf_medic.c.finished,
                                            func.date_format(inf_medic.c.created_at, "%d/%m"))
                                    .select_from(inf_medic)
                                    .join(users, inf_medic.c.user_id == users.c.id).where(
                                        or_(
                                            and_(
                                                users.c.name.like(f'%{first_name}%'),
                                                users.c.last_name.like(f'%{last_name}%')
                                            ),
                                            and_(
                                                users.c.last_name.like(f'%{last_name}%'),
                                                users.c.name.like(f'%{first_name}%')
                                            ),
                                            users.c.name.like(f'%{search_case}%'),
                                            users.c.last_name.like(f'%{search_case}%')
                                    ))
                                    .where(inf_medic.c.doc_id == userid)).fetchall()
        else:
            #revisar despues de almuerzo en donde esta el error de lista vacia en alguno de los if, revisar consulta
            if search_type == "week":
                print("entra al quinto if")
                today = datetime.now().date()
                monday = today - timedelta(days=today.weekday())
                monday_midnight = datetime.combine(monday, datetime.min.time())
              
                case_pat = conn.execute(select(inf_medic.c.id,
                                            inf_medic.c.doc_id,
                                            inf_medic.c.user_id,
                                            users.c.name,
                                            users.c.last_name,
                                            inf_medic.c.finished,
                                            func.date_format(inf_medic.c.created_at, "%d/%m"))
                                    .select_from(inf_medic)
                                    .join(users, inf_medic.c.user_id == users.c.id)
                                    .where(inf_medic.c.doc_id == userid)
                                    .where(inf_medic.c.created_at >= monday_midnight)
                                    .where(inf_medic.c.created_at <= datetime.now())).fetchall()
              
            elif search_type == "day":
                print("entra al sexto if")
                one_day_ago = datetime.combine(datetime.now() - timedelta(days=1),datetime.min.time())
                print(one_day_ago)
                case_pat = conn.execute(select(inf_medic.c.id,
                                            inf_medic.c.doc_id,
                                            inf_medic.c.user_id,
                                            users.c.name,
                                            users.c.last_name,
                                            inf_medic.c.finished,
                                            func.date_format(inf_medic.c.created_at, "%d/%m"))
                                    .select_from(inf_medic)
                                    .join(users, inf_medic.c.user_id == users.c.id)
                                    .where(inf_medic.c.doc_id == userid)
                                    .where(inf_medic.c.created_at >= one_day_ago)).fetchall()
                print(case_pat)
                
            elif search_type == "month":
                print("entra al septimo if")
                first_day_of_month = datetime.now().replace(day=1)
                first_day_of_month_midnight = datetime.combine(first_day_of_month, datetime.min.time())
              
                case_pat = conn.execute(select(inf_medic.c.id,
                                            inf_medic.c.doc_id,
                                            inf_medic.c.user_id,
                                            users.c.name,
                                            users.c.last_name,
                                            inf_medic.c.finished,
                                            func.date_format(inf_medic.c.created_at, "%d/%m"))
                                    .select_from(inf_medic)
                                    .join(users, inf_medic.c.user_id == users.c.id)
                                    .where(inf_medic.c.doc_id == userid)
                                    .where(inf_medic.c.created_at >= first_day_of_month_midnight)
                                    .where(inf_medic.c.created_at <= datetime.now())).fetchall()
                
            else:
                print("entra al octavo if")
                case_pat = conn.execute(select(inf_medic.c.id,
                                            inf_medic.c.doc_id,
                                            inf_medic.c.user_id,
                                            users.c.name,
                                            users.c.last_name,
                                            inf_medic.c.finished,
                                            func.date_format(inf_medic.c.created_at, "%d/%m"))
                                    .select_from(inf_medic)
                                    .join(users, inf_medic.c.user_id == users.c.id)
                                    .where(inf_medic.c.doc_id == userid)).fetchall()  
    list_case = []
    
    for row in case_pat:
        result_dict = {
            "id": row[0],
            "doc_id": row[1],
            "user_id": row[2],
            "name": row[3],
            "last_name": row[4],
            "finished": row[5],
            "created_at": row[6]
        }
    list_case.append(result_dict)
    data_case = []                         
    for casep in list_case:
        user_id = casep["user_id"]
        full_case = casep
        with engine.connect() as conn:
            image = conn.execute(user_image_profile.select().where(user_image_profile.c.user_id == user_id)).first()
            if image:
                file_path = f"./img/profile/{image.image_profile}.png"
                if not os.path.exists(file_path):
                    return {"error": "No existe la imagen de perfil en el sistema de archivos"}
            
                image = FileResponse(file_path)
                
                base_url = str(request.base_url)
                image_url = f"{base_url.rstrip('/')}/img/profile/{image.image_profile}.png"
                full_case["url_img_profile"] = image_url
            else:
                full_case["url_img_profile"] = None
        data_case.append(full_case)
    return data_case

@doctorhome.get("/doctor/home-dashboard/{doc_id}/")
async def dashboard_home_doctor(doc_id: int, current_user: str = Depends(get_current_user)):
    verify_rol_doctor(current_user)
    #obtener lunes de la semana actual
    monday = datetime.now() - timedelta(days=datetime.now().date().weekday())
    monday_midnight = datetime.combine(monday, datetime.min.time())
   
    # Obtener la fecha y hora del viernes pasado
    current_date = datetime.now()
    last_week_date = current_date - timedelta(days=current_date.weekday(), weeks=1)
    last_friday = last_week_date + timedelta(days=4)
    last_friday_at_2359 = datetime.combine(last_friday, datetime.max.time())

    #obtener lunes de la semana pasada
    current_date = datetime.now()
    last_week_date = current_date - timedelta(days=current_date.weekday(), weeks=1)
    last_monday = last_week_date - timedelta(days=last_week_date.weekday())
    last_monday_midnight = datetime.combine(last_monday, datetime.min.time())
    
    with engine.connect() as conn:
        pat_data_last_week = len(conn.execute(inf_medic.select()
                                         .where(inf_medic.c.doc_id==doc_id)
                                         .where(inf_medic.c.created_at.between(last_monday_midnight, last_friday_at_2359))).fetchall())
        pat_data_this_week = len(conn.execute(inf_medic.select()
                                         .where(inf_medic.c.doc_id==doc_id)
                                         .where(inf_medic.c.created_at.between(monday_midnight, datetime.now()))).fetchall())
        pat_data_total = len(conn.execute(inf_medic.select()
                                         .where(inf_medic.c.doc_id==doc_id)).fetchall())
       
        
        pat_exam_last_week = len(conn.execute(inf_medic.select()
                                              .join(medical_exam, inf_medic.c.exam_id == medical_exam.c.id)
                                              .where(inf_medic.c.doc_id==doc_id)
                                              .where(medical_exam.c.done == 1)
                                              .where(inf_medic.c.created_at.between(monday_midnight, last_friday_at_2359))).fetchall())
        pat_exam_this_week = len(conn.execute(inf_medic.select()
                                              .join(medical_exam, inf_medic.c.exam_id == medical_exam.c.id)
                                              .where(inf_medic.c.doc_id==doc_id)
                                              .where(medical_exam.c.done == 1)
                                              .where(inf_medic.c.created_at.between(monday_midnight, datetime.now()))).fetchall())
        pat_exam_total= len(conn.execute(inf_medic.select()
                                              .join(medical_exam, inf_medic.c.exam_id == medical_exam.c.id)
                                              .where(inf_medic.c.doc_id==doc_id)
                                              .where(medical_exam.c.done == 1)).fetchall())
        
        return JSONResponse(content={
            "number_patients":{
                "last_week": pat_data_last_week,
                "this_week": pat_data_this_week,
                "total": pat_data_total
            },
            "number_exams":{
                "last_week": pat_exam_last_week,
                "this_week": pat_exam_this_week,
                "total": pat_exam_total
            }
        }, status_code=status.HTTP_200_OK)
        
        
        