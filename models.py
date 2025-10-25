from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    author = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now)
