from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, Boolean, DateTime, Numeric, TIMESTAMP
from sqlalchemy.sql.functions import func
from config.db import engine, meta_data

usercontact = Table("usercontact", meta_data,
                    Column("id", Integer, primary_key=True),
                    Column("user_id", Integer, ForeignKey("users.id")),
                    Column("phone", String(20), nullable=True),
                    Column("country", String(191), nullable=True),
                    Column("state", String(191), nullable=True),
                    Column("direction", String(191),nullable=True),
                    Column("created_at", TIMESTAMP, nullable=True, default=func.now()))
 

meta_data.create_all(engine, checkfirst=True)