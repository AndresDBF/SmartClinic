from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, Boolean, DateTime, Numeric, TIMESTAMP
from sqlalchemy.sql.functions import func
from config.db import engine, meta_data

calification_doc = Table("calification_doc",meta_data,
                   Column("id",Integer,primary_key=True,nullable=False),
                   Column("doctor_id", Integer, ForeignKey("users.id"), nullable=False),
                   Column("points", String(30), nullable=False),
                   Column("notes", String(191), nullable=True),
                   Column("experience", String(20), nullable=False)
)

meta_data.create_all(engine, checkfirst=True)