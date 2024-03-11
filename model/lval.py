from sqlalchemy import inspect, create_engine, Column, Table
from sqlalchemy.sql.sqltypes import String, Integer
from sqlalchemy.sql import select
from config.db import engine, meta_data

# Define la tabla lval
lval = Table(
    "lval",
    meta_data,
    Column("id", Integer, primary_key=True, nullable=False),
    Column("tipval", String(10), nullable=False),
    Column("description", String(191), nullable=False)
)

existing_lval = inspect(engine).has_table("lval")

# Si la tabla lval no existe, la crea y luego inserta los datos iniciales
if not existing_lval:
    meta_data.create_all(engine)
    
    # Inserta los datos iniciales en la tabla lval
    with engine.connect() as conn:
        insert_stmt = lval.insert().values([
            {"id": 1, "tipval": "PRNOTF", "description": "Alta"},
            {"id": 2, "tipval": "PRNOTF", "description": "Media"},
            {"id": 3, "tipval": "PRNOTF", "description": "Baja"},
            {"id": 4, "tipval": "CALDOC", "description": "Muy mala"},
            {"id": 5, "tipval": "CALDOC", "description": "Mala"},
            {"id": 6, "tipval": "CALDOC", "description": "Buena"},
            {"id": 7, "tipval": "CALDOC", "description": "Muy Buena"},
            {"id": 8, "tipval": "CALDOC", "description": "Excelente"},
        ])
        conn.execute(insert_stmt)
        conn.commit()
