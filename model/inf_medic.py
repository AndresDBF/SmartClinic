from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, Boolean, DateTime, Numeric
from config.db import engine, meta_data

inf_medic = Table("inf_medic",meta_data,
                   Column("id",Integer,primary_key=True,nullable=False),
                   Column("diag_id", Integer, ForeignKey("diagnostic.id"), nullable=False),
                   Column("case", String(191), nullable=False),
                   Column("disease", String(191), nullable=False),
                   Column("imp_diag", String(191), nullable=False),
                   Column("background", String(191), nullable=False),
                   Column("medication", String(191), nullable=False),
                   Column("exam",String(191), nullable=False)
)

meta_data.create_all(engine)