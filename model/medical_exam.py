from sqlalchemy import Column, Table, func, DateTime, Index, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, Boolean, TIMESTAMP
from config.db import engine, meta_data

medical_exam = Table("medical_exam", meta_data, 
                     Column("id", Integer, primary_key=True, nullable=False),
                     Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
                     Column("description_exam", String(300), nullable=False),
                     Column("done", Boolean, nullable=False, default=False),
                     Column("created_at", TIMESTAMP, nullable=False)
)

meta_data.create_all(engine)
