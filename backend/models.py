from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    product = Column(String, index=True, nullable=True)
    original_text = Column(String, nullable=False)
    original_language = Column(String, nullable=True)
    translated_text = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)
    was_reviewed = Column(Boolean, default=False, nullable=False) 
    status = Column(String, default='published', nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    