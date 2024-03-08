from sqlalchemy import Column, Table, TIMESTAMP
from sqlalchemy.sql.sqltypes import String, Integer, Boolean, Numeric, Date
from sqlalchemy.schema import CreateTable, MetaData
from sqlalchemy.sql.functions import func
from config.db import engine, meta_data

# Definir la tabla de usuarios
users = Table("users", meta_data,
              Column("id", Integer, primary_key=True),
              Column("username", String(191), nullable=False),
              Column("email", String(191), nullable=False),
              Column("password", String(191), nullable=False),
              Column("name", String(191), nullable=False),
              Column("last_name", String(191), nullable=False),
              Column("birthdate", Date, nullable=False),
              Column("gender", String(1), nullable=False, default="M"),
              Column("tipid", String(1), nullable=False, default="V"),
              Column("identification", Numeric, nullable=False),
              Column("disabled", Boolean, nullable=False, default=False),
              Column("verify_ident", Boolean, nullable=False, default=False),
              Column("created_at", TIMESTAMP, nullable=False, server_default=func.now())
)

# Crear todas las tablas en la base de datos, verificando primero si ya existen
meta_data.create_all(engine, checkfirst=True)
""" 
# Verificar si la columna "created_at" ya existe en la tabla
if not users.columns.get('created_at'):
    # Agregar la nueva columna "created_at"
    created_at_column = Column("created_at", TIMESTAMP, nullable=False)
    alter_table(users).append_column(created_at_column)
    users.create(engine)
    print("Columna 'created_at' agregada correctamente.")
else:
    print("La columna 'created_at' ya existe en la tabla.") """



