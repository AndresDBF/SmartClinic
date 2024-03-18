from sqlalchemy import Column, Table, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import String, Integer, Boolean, DateTime, Numeric, TIMESTAMP
from sqlalchemy.sql.functions import func
from config.db import engine, meta_data

agora_rooms = Table("agora_rooms",meta_data,
                    Column("id", Integer, nullable=False, primary_key=True),
                    Column("romm_id", String(50), nullable=False, unique=True),
                    Column("user_id_creator", Integer, ForeignKey("users.id"), nullable=False),
                    Column("user_id_invite", Integer,ForeignKey("users.id"), nullable=False),
)

meta_data.create_all(engine, checkfirst=True)