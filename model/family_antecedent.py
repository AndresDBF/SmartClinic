from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from config.db import meta_data, engine


family_antecedent = Table("family_antecedent", meta_data, 
                          Column("id", Integer, primary_key=True, nullable=False),
                          Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
                          Column("disease_mother_value", String(250), nullable=False),
                          Column("disease_mother_text", String(250), nullable=True),
                          Column("disease_father_value", String(250), nullable=False),
                          Column("disease_father_text", String(250), nullable=True),
                          Column("created_at", TIMESTAMP, nullable=False, server_default=func.now())
)

meta_data.create_all(engine)