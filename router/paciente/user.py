import smtplib
import poplib
import hashlib
import setuptools
import os
from fastapi import APIRouter, Response, status, HTTPException, Depends, Path, Form, UploadFile, File, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse

from config.db import engine

from model.user import users
from model.usercontact import usercontact
from model.images.user_image_profile import user_image_profile
from model.roles.roles import roles
from model.roles.user_roles import user_roles

from schema.user_schema import UserSchema, DataUser, UserContact, verify_email, UserUpdated, UserContactUpdated, UserImageProfile
from schema.userToken import UserInDB, User, OAuth2PasswordRequestFormWithEmail

from passlib.context import CryptContext
from pydantic import EmailStr
from pydantic import ValidationError

from sqlalchemy import insert, select, func
from sqlalchemy.exc import IntegrityError

from werkzeug.security import generate_password_hash, check_password_hash
from typing import List, Union
from datetime import datetime,timedelta, date
from jose import jwt, JWTError

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from uuid import uuid4

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from typing import List, Optional

from router.logout import SECRET_KEY, ALGORITHM, get_current_user

security = HTTPBearer()

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

user = APIRouter(tags=['Users'], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

user.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Definir la ruta absoluta de la carpeta de imágenes estáticas
img_directory = os.path.abspath(os.path.join(project_root, 'SmartClinic', 'img', 'profile'))

# Montar la carpeta de imágenes estáticas
user.mount("/img", StaticFiles(directory=img_directory), name="img")


#instancia 
oauth2_scheme = OAuth2PasswordBearer("/api/user/login")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@user.get("/")
async def root():
    
    return setuptools.__version__

@user.get("/api/user/test", response_model=List[UserSchema])
async def get_users():
    with engine.connect() as conn:
        result = conn.execute(users.select()).fetchall()
        result2 = conn.execute(select(users.c.id, users)).first()
        
        return result
    
@user.get("/api/user/test/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def get_user(user_id: str):
    with engine.connect() as conn:
        result = conn.execute(users.select().where(users.c.id == user_id)).first()         
        return result
    
#----------------------------------CREAR USUARIO---------------------------------------------  
def verify_username_email(username: str, email: str): 
    
    with engine.connect() as conn:        
        query_user = conn.execute(users.select().where(users.c.username == username)).first()
        query_email = conn.execute(users.select().where(users.c.email == email)).first()
        if query_user is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este nombre de usuario no se encuentra disponible")
        if query_email is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este Correo se encuentra en uso")
        if query_email is not None and query_user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario y correo ya existen")
        else:
            return True

def verify_iden(tipid: str, gender: str):
    if tipid != "V" and tipid != "J" and tipid != "E":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El tipo de identificacion '{tipid}' no es correcto")
    if gender != "M" and gender != "F":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El Genero proporcionado '{gender}' no es correcto")
    return True
    
@user.post("/api/user/register/",  status_code=status.HTTP_201_CREATED)
async def create_user(tiprol:str, request: Request,username: str = Form(...),email: EmailStr = Form(...),password: str = Form(...),name: str = Form(...),last_name: str = Form(...),gender: str = Form(...),birthdate: date = Form(...),tipid: str = Form(...),identification: int = Form(...),phone: str = Form(...),country: str = Form(...),state: str = Form(...),direction: str = Form(...),image: UploadFile = File(None)):
    try:
        role = verify_tiprol(tiprol)
        print(role)
        with engine.connect() as conn:
            name = name.title()
            last_name = last_name.title()
            tipid = tipid.title()
            gender = gender.title()
            last_id = conn.execute(select(func.max(users.c.id))).scalar()
            last_contact_id = conn.execute(select(func.max(usercontact.c.id))).scalar()
            new_user = {"id": last_id,"username": username,"email": email,"verify_email": verify_email,"password": password,"name": name,"last_name": last_name,"gender": gender,"birthdate": birthdate,"tipid": tipid,"identification": identification,"disabled": False, "verify_ident": False}
            new_contact_user = {"id": last_contact_id,"user_id": 1,"phone": phone,"country": country,"state": state,"direction": direction}
            query_roles = conn.execute(roles.select().where(roles.c.role_name == role)).first()
            print(query_roles)
            if verify_username_email(username, email):
                if verify_iden(tipid, gender):
                    if last_id is not None:
                        id = last_id + 1
                        id_contact = last_contact_id + 1
                    else:
                        id = 1 
                        id_contact = 1
                    hashed_password = pwd_context.hash(password)
                    new_user["password"] = hashed_password
                    if role == "Patient" or role == "Doctor":
                        print("entra en el primer if")
                        stmt = insert(users).values(username=new_user["username"],email=new_user["email"],password=new_user["password"],name=new_user["name"],last_name=new_user["last_name"],gender=new_user["gender"],birthdate=new_user["birthdate"],tipid=new_user["tipid"],identification=new_user["identification"],disabled=new_user["disabled"], verify_ident=new_user["verify_ident"])
                        result = conn.execute(stmt)
                        userid = result.lastrowid
                        conn.commit()
                    if role == "Admin":
                        print("entra en el segundo if ")
                        stmt = insert(users).values(username=new_user["username"],email=new_user["email"],password=new_user["password"],name=new_user["name"],last_name=new_user["last_name"],gender=new_user["gender"],birthdate=new_user["birthdate"],tipid=new_user["tipid"],identification=new_user["identification"],disabled=True, verify_ident=True)
                        result = conn.execute(stmt)
                        userid = result.lastrowid
                        conn.commit()
                    print(userid)
                    conn.execute(user_roles.insert().values(user_id=userid, role_id=query_roles[0]))
                    conn.commit()

                    send_verification_email(email, userid, request)

                    new_contact_user["id"] = id_contact
                    new_contact_user['user_id'] = userid
                    save_contact = usercontact.insert().values(new_contact_user)
                    conn.execute(save_contact)
                    conn.commit()
#-----------------------------inserta la imagen de perfil-------------------------------------------------------------------------
                    if image is not None:
                        if image.filename != '':
                            try:
                                if image.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
                                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser una imagen JPEG, JPG o PNG")
                                content_profile_image = await image.read()
                                pr_photo = hashlib.sha256(content_profile_image).hexdigest()
                                with open(f"img/profile/{pr_photo}.png", "wb") as file_ident:
                                    file_ident.write(content_profile_image)
                                with engine.connect() as conn:
                                    query = user_image_profile.insert().values(user_id=userid, image_profile_original=image.filename, image_profile=pr_photo)
                                    conn.execute(query)
                                    conn.commit()     
                                file_path_prof = f"./img/profile/{pr_photo}"
                                image_ident = FileResponse(file_path_prof)  
                                base_url = str(request.base_url)
                                image_url_ident = f"{base_url.rstrip('/')}/img/profile/{pr_photo}.png"              
                            except IntegrityError:
                                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen ya existe")
                          
                            if pwd_context.verify(password, hashed_password):
                            
                                user = authenticate_user(email, password)
                                access_token_expires = timedelta(minutes=30)
                                access_token_jwt = create_token({"sub": user.email}, access_token_expires)
                                created_user = {
                                    "user":{
                                        "id": userid,
                                        "username": new_user["username"],
                                        "email": new_user["email"],
                                        "name": new_user["name"],
                                        "last_name": new_user["last_name"],
                                        "gender": new_user["gender"],
                                        "birthdate": new_user["birthdate"],
                                        "tipid": new_user["tipid"],
                                        "identification": new_user["identification"],
                                        "disabled": new_user["disabled"],
                                        "urlimage":  image_url_ident      
                                    },
                                    "token":{
                                        "access_token": access_token_jwt,
                                        "token_types": "bearer"
                                    }
                                }
                            
                                return created_user  
#--------------------------------------------------------------------------------------------------------------------------------------------
                    if pwd_context.verify(password, hashed_password):    
                        user = authenticate_user(email, password)
                        access_token_expires = timedelta(minutes=240)
                        access_token_jwt = create_token({"sub": user.email}, access_token_expires)
                    created_user = {
                        "user":{
                             "id": userid,
                            "username": new_user["username"],
                            "email": new_user["email"],
                            "name": new_user["name"],
                            "last_name": new_user["last_name"],
                            "gender": new_user["gender"],
                            "birthdate": new_user["birthdate"],
                            "tipid": new_user["tipid"],
                            "identification": new_user["identification"],
                            "disabled": new_user["disabled"],
                            "urlimage": None
                        },
                        "token":{
                            "access_token": access_token_jwt,
                            "token_types": "bearer"
                        }
                    }
                    return created_user
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
#--------------------------LOGIN DE USUARIO ----------------------------------------
#------------------Dependencias para token ------------------------------

def authenticate_user(email, password):
    user = get_user(email)

    if not user:
        raise HTTPException(status_code=401, detail="No se pueden validar las credenciales", headers={"www-authenticate": "Bearer"})
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="No se pueden validar las credenciales", headers={"www-authenticate": "Bearer"})
    return user
def get_user(email):
    with engine.connect() as conn:
        result = conn.execute(users.select().where(users.c.email == email)).first()
        if result:
             #para que se devuelva el conjunto de datos de la base de datos
   
            return result
        return []
def verify_password(plane_password, hashed_password):

    return pwd_context.verify(plane_password,hashed_password) #verificando que el texto plano sea igual que el encriptado
def create_token(data: dict, time_expire: Union[datetime,None] = None):
    data_copy = data.copy()
    if time_expire is None:
        expires = datetime.utcnow() +  timedelta(minutes=15)#datetime.utcnow() trae la hora de ese instante
    else:
        expires = datetime.utcnow() + time_expire
    print(expires)
    data_copy.update({"exp": expires})
    token_jwt = jwt.encode(data_copy, key=SECRET_KEY, algorithm=ALGORITHM)

    return token_jwt

def verify_tiprol(tiprol: str):
    tiprol = tiprol.lower()
    with engine.connect() as conn:
        if tiprol == "patient":
            role = conn.execute(roles.select().where(roles.c.role_name == tiprol)).first()
            namerole = role.role_name
            return namerole
        if tiprol == "doctor":
            role = conn.execute(roles.select().where(roles.c.role_name == tiprol)).first()
            namerole = role.role_name
            return namerole
        if tiprol == "admin":
            role = conn.execute(roles.select().where(roles.c.role_name == tiprol)).first()
            namerole = role.role_name
            return namerole
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="el parametro tiprol no encuentra el tipo de rol")
    

@user.post("/api/user/login/", status_code=status.HTTP_200_OK)
async def user_login(tiprol: str, email: str = Form(...), password: str = Form(...)):
        if tiprol is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El parametro query es requerido")            
        try:
            role = verify_tiprol(tiprol)
            with engine.connect() as conn:
                result = conn.execute(users.select().where(users.c.email == email)).first()
                if result is not None:
                    id = result.id
                    query_role = conn.execute(roles.select().
                                    join(user_roles, roles.c.role_id == user_roles.c.role_id).
                                    join(users, user_roles.c.user_id == users.c.id).
                                    where(user_roles.c.user_id == result[0]).where(roles.c.role_name==tiprol)).first()
                    if query_role is None:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El tipo de usuario no coincide con el usuario registrado")
                    stored_password_hash = result[3]
                    if pwd_context.verify(password, stored_password_hash):
                    
                        user = authenticate_user(email, password)
                        access_token_expires = timedelta(minutes=30)
                        access_token_jwt = create_token({"sub": user.email}, access_token_expires)
        
                        return {
                            "id_user": id,
                            "tip_user": role,
                            "access_token": access_token_jwt,
                            "token_types": "bearer"
                        }
                    else:
                        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
                else:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
        except ValidationError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no se ha encontrado usuarios")
        
#--------------------------------EDITAR DATOS DE USUARIO-------------------------------------------

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials  # Obtiene el token de las credenciales
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales de Autenticacion Invalidas")
        # Puedes hacer alguna lógica adicional para verificar el usuario si es necesario
        return email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Invalido")

@user.get("/api/user/show/{user_id}")
async def edit_user(user_id: int, request: Request, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        user = conn.execute(users.select().where(users.c.id == user_id)).first()
        user_contact = conn.execute(usercontact.select().where(usercontact.c.user_id == user_id)).first()
        profile = conn.execute(select(user_image_profile.c.image_profile_original,
                                    user_image_profile.c.image_profile).select_from(user_image_profile).
                               join(users, user_image_profile.c.user_id==users.c.id).
                               where(users.c.id == user_id)).first()
       
    if profile is not None:
        print(profile)
        file_path_file = f"./img/profile/{profile.image_profile}.png"
        if not os.path.exists(file_path_file):
            return {"error": "La imagen de perfil no existe"}
        prof_img = FileResponse(file_path_file)
        base_url = str(request.base_url)
        url_image = f"{base_url.rstrip('/')}/img/profile/{profile.image_profile}.png" 
        return {
            "users":{
                "id": user[0],
                "username": user[1],	
                "email": user[2],		
                "name": user[4],	
                "last_name": user[5],		
                "birthdate": user[6],
                "gender": user[7],	
                "tipid": user[8],		
                "identification": user[9]
            },
            "usercontact":{
                "phone": user_contact[2],	
                "country": user_contact[3],	
                "state": user_contact[4],	
                "direction": user_contact[5]
            },
            "image_profile":{
                "url_profile": url_image
            }
        }
    return {
        "users":{
            "id": user[0],
            "username": user[1],	
            "email": user[2],		
            "name": user[4],	
            "last_name": user[5],		
            "birthdate": user[6],
            "gender": user[7],	
            "tipid": user[8],		
            "identification": user[9]
        },
        "usercontact":{
            "phone": user_contact[2],	
            "country": user_contact[3],	
            "state": user_contact[4],	
            "direction": user_contact[5]
        }
    }
    
@user.put("/api/user/update/{user_id}")  
async def create_user(
    user_id: int,
    tiprol:str,
    request: Request,
    username: str = Form(None),
    email: EmailStr = Form(None),
    name: str = Form(None),
    last_name: str = Form(None),
    gender: str = Form(None),
    birthdate: date = Form(None),
    tipid: str = Form(None),
    identification: int = Form(None),
    phone: str = Form(None),
    country: str = Form(None),
    state: str = Form(None),
    direction: str = Form(None),
    image: UploadFile = File(None),  current_user: str = Depends(get_current_user)):
    
    update_user = {}
    update_contact_user = {}
    
    if username:
        update_user["username"] = username
    if email:
        update_user["email"] = email
    if name:
        update_user["name"] = name
    if last_name:
        update_user["last_name"] = last_name
    if gender:
        gender = gender.title()
        if gender != "M" and gender != "F":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El Genero proporcionado '{gender}' no es correcto")
        update_user["gender"] = gender
    if birthdate:
        update_user["birthdate"] = birthdate
    if tipid:
        tipid = tipid.title()
        if tipid != "V" and tipid != "J" and tipid != "E":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El tipo de identificacion '{tipid}' no es correcto")
        update_user["tipid"] = tipid     
    if identification:
        update_user["identification"] = identification
    if phone:
        update_contact_user["phone"] = phone
    if country:
        update_contact_user["country"] = country
    if state:
        update_contact_user["state"] = state
    if direction:
        update_contact_user["direction"] = direction
        
    with engine.connect() as conn:
        #verificando email y username
        query_existing_user = conn.execute(users.select().where(users.c.username == username).where(users.c.id != user_id)).first()
      
        query_existing_email = conn.execute(users.select().where(users.c.email == email).where(users.c.id != user_id)).first()
        if query_existing_user is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El usuario {username} ya existe")
        if query_existing_email is not None:             
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El email {email} ya se encuentra en uso")
        #insertando data 
        if image is not None:
          
            if image.filename != '':
                try:
                    if image.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser una imagen JPEG, JPG o PNG")
                    content_profile_image = await image.read()
                    pr_photo = hashlib.sha256(content_profile_image).hexdigest()
                    with open(f"img/profile/{pr_photo}.png", "wb") as file_ident:
                        file_ident.write(content_profile_image)
                   
                    file_path_prof = f"./img/profile/{pr_photo}"
                    image_ident = FileResponse(file_path_prof)  
                    base_url = str(request.base_url)
                    image_url = f"{base_url.rstrip('/')}/img/profile/{pr_photo}.png" 
                    
                    conn.execute(user_image_profile.update().
                                    where(user_image_profile.c.user_id==user_id).
                                    values(image_profile_original=image.filename, image_profile=pr_photo))
                    conn.commit()
                except IntegrityError:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen ya existe")
        
        try:
            if update_user:
                conn.execute(users.update().where(users.c.id == user_id).values(update_user))
                conn.commit()
            if update_contact_user:
                conn.execute(usercontact.update().where(usercontact.c.user_id == user_id).values(update_contact_user))
                conn.commit()       
        except IntegrityError: 
            return Response(content="No se actualizaron datos", status_code=status.HTTP_304_NOT_MODIFIED)
        if email is not None:
            send_verification_email(email, user_id, request)
        
    return Response(content="Cuenta actualizada correctamente", status_code=status.HTTP_200_OK)

#---------------codigo guardado para envio de correo de verificacion---------------------   
    
def send_verification_email(email, user_id, request: Request):
    sender_email = "andrespruebas222@gmail.com"
    sender_name = "Andres Becerra"
    subject = "Verificación de cuenta"
    base_url = str(request.base_url)
    verification_link = f"{base_url.rstrip('/')}/api/verify/{user_id}"

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = subject

    text = f"Para verificar tu cuenta, haz clic en el siguiente enlace: {verification_link}"
    html = f"<p>Para verificar tu cuenta, haz clic en el siguiente enlace: <a href='{verification_link}'>Verificar cuenta</a></p>"

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, "vhvcinzspvlwoftc")  # Coloca tu contraseña aquí
        server.send_message(message)
    return JSONResponse(content={"saved": True, "message": "correo enviado correctamente"}, status_code=status.HTTP_200_OK)
    
#---------------------para verificar el token------------------------------------------------------------
