from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, Boolean, DateTime, Numeric, TIMESTAMP
from sqlalchemy.sql.functions import func
from config.db import engine, meta_data

inf_medic = Table("inf_medic",meta_data,
                   Column("id",Integer,primary_key=True,nullable=False),
                   Column("doc_id", Integer, ForeignKey("users.id"), nullable=False),
                   Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
                   Column("ante_id", Integer, ForeignKey("person_antecedent.id"), nullable=False),
                   Column("exam_id", Integer, ForeignKey("medical_exam.id"), nullable=False),
                   Column("atent_id", String(20), nullable=False),
                   Column("case", String(191), nullable=False),
                   Column("disease", String(191), nullable=False),
                   Column("imp_diag", String(191), nullable=False),
                   Column("medication", String(191), nullable=False),
                   Column("created_at", TIMESTAMP, nullable=True)
)


meta_data.create_all(engine, checkfirst=True)