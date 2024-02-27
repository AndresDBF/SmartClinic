@user.post("/api/user/register", status_code=status.HTTP_201_CREATED)
async def create_user(data_user: UserSchema, data_user_contact: UserContact, image: UploadFile = File()):

    print(data_user)
    print(data_user_contact)
    try:
        with engine.connect() as conn:
            data_user.name = data_user.name.title()
            data_user.last_name = data_user.last_name.title()
            data_user.tipid = data_user.tipid.title()
            data_user.gender = data_user.gender.title()
            last_id = conn.execute(select(func.max(users.c.id))).scalar()
            last_contact_id = conn.execute(select(func.max(usercontact.c.id))).scalar()
            
            
            if verify_username_email(data_user.username, data_user.email, data_user.verify_email):
                if verify_ident(data_user.tipid, data_user.gender):
                    if last_id is not None:
                        data_user.id = last_id + 1
                        data_user_contact.id = last_contact_id + 1
                    else:
                        data_user.id = 1 
                        data_user_contact.id = 1
                    # Hashea la contraseña antes de almacenarla en la base de datos
                    
                    hashed_password = pwd_context.hash(data_user.password)
                    data_user.password = hashed_password
                    new_user = data_user.dict()
                    new_contact_user = data_user_contact.dict()
   
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
                    user_id = result.lastrowid
                    conn.commit()
                    # Agregar el 'id' del usuario al diccionario de detalles de contacto
                    new_contact_user['user_id'] = user_id
                    # Insertar los detalles de contacto con la clave foránea user_id
                    save_contact = usercontact.insert().values(new_contact_user)
                    conn.execute(save_contact)
                    conn.commit()
                    
                    if image is not None:
                        insert_profile_image(image, user_id)
                    created_user = UserSchema(**new_user)
                    return created_user  # Devolver el objeto UserSchema completo
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))