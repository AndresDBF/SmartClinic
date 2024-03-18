from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from config.db import meta_data, engine

personal_habit = Table("personal_habit", meta_data,
                      Column("id", Integer, primary_key=True, nullable=False),
                      Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
                      Column("consumed", String(250), nullable=True),
                      Column("created_at", TIMESTAMP, nullable=True)
)

meta_data.create_all(engine, checkfirst=True)