from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP, Boolean, Time, Float
from sqlalchemy.sql import func
from config.db import meta_data, engine

pharmacy_contact  = Table("pharmacy_contact", meta_data,
                      Column("id", Integer, primary_key=True, nullable=False),
                      Column("pharmacy_id", Integer, ForeignKey("pharmacy.id"), nullable=False),
                      Column("name_direction", String(191), nullable=False),
                      Column("desc_direction", String(250), nullable=False),
                      Column("phone", String(20), nullable=False),
                      Column("opening", Time(timezone=False), nullable=False),
                      Column("closing", Time(timezone=False), nullable=False),
                      Column("open", Boolean, default=True, nullable=False),
                      Column("coordinates", String(191), nullable=False),
                      Column("created_at", TIMESTAMP, nullable=False)
                      
)

meta_data.create_all(engine, checkfirst=True)   