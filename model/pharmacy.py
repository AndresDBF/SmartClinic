from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP, Boolean, Time, Float
from sqlalchemy.sql import func
from config.db import meta_data, engine

pharmacy  = Table("pharmacy", meta_data,
                      Column("id", Integer, primary_key=True, nullable=False),
                      Column("name", String(191), nullable=False),
                      Column("details", String(250), nullable=False),
                      Column("created_at", TIMESTAMP, nullable=False)
)

meta_data.create_all(engine, checkfirst=True)   