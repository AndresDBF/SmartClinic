from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP
from sqlalchemy.sql.functions import func
from config.db import meta_data, engine

user_image = Table("user_image", meta_data,
                    Column("id", Integer, primary_key=True),
                    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
                    Column("image_ident_original", String(191), nullable=False),
                    Column("image_self_original", String(191), nullable=False),
                    Column("image_ident", String(191), nullable=False),
                    Column("image_self", String(191), nullable=False),
                    Column("created_at", TIMESTAMP, nullable=False, server_default=func.now())
)

meta_data.create_all(engine, checkfirst=True)