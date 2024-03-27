from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP
from sqlalchemy.sql.functions import func
from config.db import meta_data, engine

pharmacy_image = Table("pharmacy_image", meta_data,
                    Column("id", Integer, primary_key=True),
                    Column("pharmacy_id", Integer, ForeignKey("pharmacy.id"), nullable=False),
                    Column("image_original", String(191), nullable=False),
                    Column("image", String(191), nullable=False),
                    Column("created_at", TIMESTAMP, nullable=False)
)

meta_data.create_all(engine, checkfirst=True)