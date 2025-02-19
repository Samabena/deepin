from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, UniqueConstraint
from app.db.database import Base
from datetime import datetime

class Registration(Base):
    __tablename__ = "registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    whatsapp_number = Column(String, nullable=False)
    email = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    preferred_course = Column(String, nullable=False)
    agreement = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now)

# Enforce UNIQUE constraint on (email, preferred_course)
    __table_args__ = (UniqueConstraint("email", "preferred_course", name="unique_email_course"),)
    