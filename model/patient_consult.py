from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, DateTime
from config.db import engine, meta_data

patient_consult = Table("patient_consult",meta_data,
                   Column("id",Integer,primary_key=True,nullable=False),
                   Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
                   Column("tipconsult_id",Integer, ForeignKey("tip_consult.id"), nullable=False),
                   Column("consult_date", DateTime, nullable=False)
)

meta_data.create_all(engine)