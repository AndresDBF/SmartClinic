from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, Boolean, DateTime, Numeric, TIMESTAMP
from sqlalchemy.sql.functions import func
from config.db import engine, meta_data

agora_rooms = Table("agora_rooms",meta_data,
                    Column("id", Integer, nullable=False, primary_key=True),
                    Column("rooms", String(191), nullable=False),
                    Column("participants", String(191), nullable=False)
)

meta_data.create_all(engine, checkfirst=True)