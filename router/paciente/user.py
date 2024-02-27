import base64
from fastapi import APIRouter, Response, status, HTTPException, Depends, Path, Form, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from config.db import engine
from model.user import users
from model.usercontact import usercontact
from model.images.user_image_profile import user_image_profile
from schema.user_schema import UserSchema, DataUser, UserContact, verify_email, UserUpdated, UserContactUpdated, UserImg
from schema.userToken import UserInDB, User, OAuth2PasswordRequestFormWithEmail
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy import insert, select, func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List, Union
from pydantic import ValidationError
from datetime import datetime,timedelta, date
from jose import jwt, JWTError
from typing import Optional

user = APIRouter(tags=['Users'], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

#instancia 
oauth2_scheme = OAuth2PasswordBearer("/api/user/login")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = "0d227dc4d6ac7f607f532c85f5d8770215f3aa12398645b3bb74f09f1ebcbd51"
ALGORITHM = "HS256"

@user.get("/")
async def root():
    return "pruebas"

@user.get("/api/user", response_model=list[UserSchema])
async def get_users():
    with engine.connect() as conn:
        result = conn.execute(users.select()).fetchall()
        result2 = conn.execute(select(users.c.id, users)).first()
        
        return result
    
@user.get("/api/user/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def get_user(user_id: str):
    with engine.connect() as conn:
        result = conn.execute(users.select().where(users.c.id == user_id)).first()         
        return result
    
#----------------------------------CREAR USUARIO---------------------------------------------  
def verify_username_email(username: str, email: str, verify_email: str): 
    if email != verify_email:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="los correos electronicos no coinciden")
    
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

def verify_ident(tipid: str, gender: str):
    if tipid != "V" and tipid != "J" and tipid != "E":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El tipo de identificacion '{tipid}' no es correcto")
    if gender != "M" and gender != "F":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El Genero proporcionado '{gender}' no es correcto")
    return True

async def insert_profile_image(image: UploadFile, user_id: int):
    try:
        print("entra en el try de insertar imagen")
        if image.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser una imagen JPEG, JPG o PNG")
        
        # Leer el contenido de la imagen
        content_profile_image = await image.read()
        print("lee la imagen")
        # Guardar la imagen en el sistema de archivos
        with open(f"img/profile/{image.filename}", "wb") as file_ident:
            file_ident.write(content_profile_image)
        print("inserta la imagen en el sistema de archivos")
        with engine.connect() as conn:
            query = user_image_profile.insert().values(
                user_id=user_id,
                image_profile=image.filename,
              
            )
            conn.execute(query)
            conn.commit()
            print("inserta la imagen en la bd ")
        # Leer el contenido de la imagen en base64
        with open(f"img/profile/{image.filename}", "rb") as file_ident:
            base64_image = base64.b64encode(file_ident.read()).decode('utf-8')

        # Devolver la imagen en base64 como parte de la respuesta JSON
        return {
            "saved": True,
            "message": "Imagen guardada correctamente",
            "image_base64": base64_image
        }
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen ya existe")
    
@user.post("/api/user/register",  status_code=status.HTTP_201_CREATED)
async def create_user(username: str = Form(...),
                    email: EmailStr = Form(...),
                    verify_email: EmailStr = Form(...),
                    password: str = Form(...),
                    name: str = Form(...),
                    last_name: str = Form(...),
                    gender: str = Form(...),
                    birthdate: date = Form(...),
                    tipid: str = Form(...),
                    identification: int = Form(...),
                    disabled: bool = Form(...),
                    phone: str = Form(...),
                    country: str = Form(...),
                    state: str = Form(...),
                    direction: str = Form(...),
                    image: UploadFile = File(...)):
    print(image)
    try:
        with engine.connect() as conn:
            name = name.title()
            last_name = last_name.title()
            tipid = tipid.title()
            gender = gender.title()
            last_id = conn.execute(select(func.max(users.c.id))).scalar()
            last_contact_id = conn.execute(select(func.max(usercontact.c.id))).scalar()
            print("viendo los id")
            print(last_id)
            print(last_contact_id)
            #creando los json
            new_user = {
                "id": last_id,
                "username": username,
                "email": email,
                "verify_email": verify_email,
                "password": password,
                "name": name,
                "last_name": last_name,
                "gender": gender,
                "birthdate": birthdate,
                "tipid": tipid,
                "identification": identification,
                "disabled": disabled
            }
            new_contact_user = {
                "id": last_contact_id,
                "user_id": 1,
                "phone": phone,
                "country": country,
                "state": state,
                "direction": direction
            }
            
            
            if verify_username_email(username, email, verify_email):
                if verify_ident(tipid, gender):
                    if last_id is not None:
                        id = last_id + 1
                        id_contact = last_contact_id + 1
                    else:
                        id = 1 
                        id_contact = 1
                    # Hashea la contraseña antes de almacenarla en la base de datos
                    
                    hashed_password = pwd_context.hash(password)
                    password = hashed_password
   
                    stmt = insert(users).values(
                        username=new_user["username"],
                        email=new_user["email"],
                        password=new_user["password"],
                        name=new_user["name"],
                        last_name=new_user["last_name"],
                        gender=new_user["gender"],
                        birthdate=new_user["birthdate"],
                        tipid=new_user["tipid"],
                        identification=new_user["identification"],
                        disabled=new_user["disabled"]
                    )
                    
                    result = conn.execute(stmt)
                    userid = result.lastrowid
                    conn.commit()
                    # Agregar el 'id' del usuario al diccionario de detalles de contacto
                    new_contact_user["id"] = id_contact
                    new_contact_user['user_id'] = userid
                    # Insertar los detalles de contacto con la clave foránea user_id
                    save_contact = usercontact.insert().values(new_contact_user)
                    conn.execute(save_contact)
                    conn.commit()
                        
                    # Obtener la imagen en base64
                    #profile_image_base64 = insert_profile_image(image, user_id)
                    #--------------------------------------------------------------------------
                    
                    
                    try:
                        print("entra en el try de insertar imagen")
                        if image.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
                            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser una imagen JPEG, JPG o PNG")
                        
                        # Leer el contenido de la imagen
                        content_profile_image = await image.read()
                        print("lee la imagen")
                        # Guardar la imagen en el sistema de archivos
                        with open(f"img/profile/{image.filename}", "wb") as file_ident:
                            file_ident.write(content_profile_image)
                        print("inserta la imagen en el sistema de archivos")
                        with engine.connect() as conn:
                            query = user_image_profile.insert().values(
                                user_id=userid,
                                image_profile=image.filename,
                            
                            )
                            conn.execute(query)
                            conn.commit()
                            print("inserta la imagen en la bd ")
                        # Leer el contenido de la imagen en base6

                        # Devolver la imagen en base64 como parte de la respuesta JSON
                        
                    except IntegrityError:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen ya existe")

                    # Agregar la imagen en base64 al objeto creado del usuario
                    created_user = {
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
                        "urlimage": f"http://localhost:8000/api/image/profile/{image.filename}"
                    }
                    return created_user  # Devolver el objeto UserSchema completo
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        

async def verify_user_data(data_user: DataUser):
    try:
        if not data_user.email or not data_user.password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="falta el usuario o contrasena")
        return data_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="debe ingresar usuario y contrasena")

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
    data_copy.update({"exp": expires})
    token_jwt = jwt.encode(data_copy, key=SECRET_KEY, algorithm=ALGORITHM)

    return token_jwt

@user.post("/api/user/login", status_code=status.HTTP_200_OK)
async def user_login(email: str = Form(...), password: str = Form(...)):
  
    try:
        with engine.connect() as conn:
            result = conn.execute(users.select().where(users.c.email == email)).first()
            if result is not None:
                stored_password_hash = result[3]
                if pwd_context.verify(password, stored_password_hash):
                 
                    user = authenticate_user(email, password)
                    access_token_expires = timedelta(minutes=30)
                    access_token_jwt = create_token({"sub": user.email}, access_token_expires)
     
                    return {
                        "access_token": access_token_jwt,
                        "token_types": "bearer"
                    }
                else:
                    
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta")
            else:
              
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario incorrecto")
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no se ha encontrado usuarios")
    
#--------------------------------EDITAR DATOS DE USUARIO-------------------------------------------
@user.get("/api/user/show/{user_id}")
async def edit_user(userid: int):
    with engine.connect() as conn:
        user = conn.execute(users.select().where(users.c.id == userid)).first()
        user_contact = conn.execute(usercontact.select().where(usercontact.c.user_id == userid)).first()
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
            "identification": user[9],
        },
        "usercontact":{
            "phone": user_contact[2],	
            "country": user_contact[3],	
            "state": user_contact[4],	
            "direction": user_contact[5]
        }
    }
    
@user.put("/api/user/update/{user_id}")  
async def update_users(userid: str, data_user: UserUpdated, data_user_contact: UserContactUpdated):
    data_user.tipid = data_user.tipid.title()
    data_user.gender = data_user.gender.title()
    with engine.connect() as conn:
        query_existing_user = conn.execute(users.select().where(users.c.username == data_user.username).where(users.c.id == userid)).first()
        query_existing_email = conn.execute(users.select().where(users.c.email == data_user.email).where(users.c.id == userid)).first()
        if query_existing_user is None:
          
            
            query_user = conn.execute(users.select().wheres(users.c.username == data_user.username).where(users.c.id != userid)).first()
       
            if query_user is not None:
                
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El usuario {data_user.username} ya existe")
        if query_existing_email is None: 
          
            query_email = conn.execute(users.select().where(users.c.email == data_user.email).where(users.c.id != userid)).first()
         
            if query_email is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El email {data_user.email} ya se encuentra en uso")
  
        ident = verify_ident(data_user.tipid, data_user.gender)
        if ident:
            new_data_user = data_user.dict()
            new_data_usercontact = data_user_contact.dict()
            conn.execute(users.update().where(users.c.id == userid).values(new_data_user))
            conn.execute(usercontact.update().where(usercontact.c.user_id == userid).values(new_data_usercontact))
            conn.commit()       
        
    return Response(content="Cuenta actualizada correctamente", status_code=status.HTTP_200_OK)

#---------------codigo guardado para envio de correo de verificacion---------------------
""" import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(email):
    sender_email = "tu_email@gmail.com"
    sender_password = "tu_contraseña"
    
    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Verificación de Cuenta"
    
    body = "Por favor, haz clic en el siguiente enlace para verificar tu cuenta: https://tudominio.com/verify"
    msg.attach(MIMEText(body, 'plain'))

    # Iniciar la conexión SMTP
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text) """
