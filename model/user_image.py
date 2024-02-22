from sqlalchemy import Column, Table, Integer, ForeignKey, String
from config.db import meta_data, engine
from model import user  # Importar la tabla 'users' desde el archivo 'users.py' en el mismo directorio

user_image = Table("user_image", meta_data,
                    Column("id", Integer, primary_key=True),
                    Column("user_id", Integer, ForeignKey("users.id"),
                    Column("image_ident", String, nullable=True),
                    Column("image_self", String, nullable=True)
                    ),  # Clave foránea a 'users'
                   # Otros campos de la tabla 'user_image' aquí
                   )

meta_data.create_all(engine)