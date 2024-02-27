'''
def detect_mime_type(file: bytes) -> str:
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file)
    return mime_type

# Función para encriptar el nombre del archivo
def encrypt_filename(filename: str) -> str:
    return hashlib.sha256(filename.encode()).hexdigest()

# Ruta para subir un archivo
@img.post("/api/upload/")
async def upload_image(file: UploadFile = File(...)):
    # Verificar si el archivo es una imagen JPEG o PNG
    if file.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen JPEG o PNG")

    # Leer el contenido del archivo
    contents = await file.read()

    # Detectar el tipo MIME del archivo
    mime_type = detect_mime_type(contents)

    # Verificar si el tipo MIME detectado coincide con el tipo MIME del archivo
    if mime_type not in ["image/jpeg", "image/jpg", "image/png"]:
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen JPEG o PNG")

    # Procesar la imagen
    img = Image.open(BytesIO(contents))

    # Encriptar el nombre del archivo
    encrypted_filename = encrypt_filename(file.filename)

    # Guardar la imagen en el servidor con el nombre encriptado
    save_path = os.path.join("uploads", encrypted_filename + os.path.splitext(file.filename)[1])
    with open(save_path, "wb") as f:
        f.write(contents)

    # Aquí puedes realizar más operaciones con la imagen si es necesario

    return {"filename": encrypted_filename, "content_type": file.content_type}
'''