from sqlalchemy import Column, Table, ForeignKey, Index
from sqlalchemy.sql.sqltypes import String, Integer, Boolean, DateTime, Numeric, TIMESTAMP
from sqlalchemy.sql.functions import func
from config.db import engine, meta_data

history_comments = Table("history_comments", meta_data, 
                 Column("id", Integer, primary_key=True, nullable=False),
                 Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
                 Column("message", String(250), nullable=False),
                 Column("created_at", TIMESTAMP, nullable=False)                
)


meta_data.create_all(engine, checkfirst=True)

indexes = [
    Index('idx_message', history_comments.c.message)
]

for index in indexes:
    index.create(bind=engine, checkfirst=True)