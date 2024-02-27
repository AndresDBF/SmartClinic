from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta_data, engine

user_image_profile = Table("user_image_profile", meta_data,
                    Column("id", Integer, primary_key=True),
                    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
                    Column("image_profile", String(191), nullable=False)
)
                   

meta_data.create_all(engine)