from sqlalchemy import Column, Table, ForeignKey, Index
from sqlalchemy.sql.sqltypes import String, Integer, DateTime, TIMESTAMP, Boolean
from sqlalchemy.sql.functions import func
from config.db import engine, meta_data

notifications = Table("notifications",meta_data,
                   Column("id",Integer,primary_key=True,nullable=False),
                   Column("user_id_receives", Integer, ForeignKey("users.id"), nullable=False),
                   Column("user_id_send", Integer, ForeignKey("users.id"), nullable=False),
                   Column("message",String(191), nullable=False),
                   Column("priority", String(6), nullable=False),
                   Column("show", Boolean, nullable=False, default=True),
                   Column("created_at", TIMESTAMP, nullable=True, default=func.now())
)

meta_data.create_all(engine, checkfirst=True)


indexes = [
    Index('idx_message', notifications.c.message),
    Index('idx_priority', notifications.c.priority),
]

# Ejecutar la creación de índices
for index in indexes:
    index.create(bind=engine, checkfirst=True)