from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP
from config.db import meta_data, engine

files_medical_exam_pat = Table("files_medical_exam_pat", meta_data,
                    Column("id", Integer, primary_key=True),
                    Column("exam_id", Integer, ForeignKey("medical_exam.id"), nullable=False),
                    Column("pdf_exam_original", String(191), nullable=True),
                    Column("image_exam_original", String(191), nullable=True),
                    Column("pdf_exam", String(191), nullable=True),
                    Column("image_exam", String(191), nullable=True),
                    Column("created_at", TIMESTAMP, nullable=False)
)
                   
meta_data.create_all(engine)