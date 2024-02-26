from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, Boolean, DateTime, Numeric
from config.db import engine, meta_data

diagnostic = Table("diagnostic",meta_data,
                   Column("id",Integer,primary_key=True,nullable=False),
                   Column("user_id", Integer, ForeignKey("users.id")),
                   Column("probl_patient", String(191), nullable=False),
                   Column("atent_id", String(20), nullable=False),
                   Column("doctor_name", String(191), nullable=False))

meta_data.create_all(engine)