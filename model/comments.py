from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, Boolean, DateTime, Numeric, TIMESTAMP
from sqlalchemy.sql.functions import func
from config.db import engine, meta_data

comments = Table("comments", meta_data, 
                 Column("id", Integer, primary_key=True, nullable=False),
                 Column("user_id_patient", Integer, ForeignKey("users.id"), nullable=False),
                 Column("user_id_doctor", Integer, ForeignKey("users.id"), nullable=False),
                 Column("enabled", Boolean, nullable=False),
                 Column("created_at", TIMESTAMP, nullable=False)                
)

meta_data.create_all(engine, checkfirst=True)