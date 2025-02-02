from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, UniqueConstraint, Column, Integer, String, Text, DateTime
from app.db.database import Base
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship



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


#Blog Posts

class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    header_image = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    author = Column(String(100), nullable=False)
    about_author = Column(Text, nullable=False)
    publication_date = Column(DateTime, nullable=False)
    reading_time = Column(Integer, nullable=False)
    introduction = Column(Text, nullable=False)
    section_1_title = Column(String(255), nullable=False)
    section_1_content = Column(Text, nullable=False)
    quote = Column(Text, nullable=True)
    section_2_title = Column(String(255), nullable=False)
    section_2_content = Column(Text, nullable=False)
    tools = Column(Text, nullable=True)
    section_3_title = Column(String(255), nullable=False)
    section_3_content = Column(Text, nullable=False)
    conclusion = Column(Text, nullable=False)
    cta = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow) 


# Users Table definition in database 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    fullname = Column(String, index=True)  # Added fullname field
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, unique=True, index=True)
    session_token = Column(String, unique=True, nullable=True)
    session_expiry = Column(DateTime, nullable=True)
    reset_token = Column(String, unique=True, nullable=True)
    profile_picture = Column(String, nullable=True) 
 

    def set_session(self, token: str):
        self.session_token = token
        self.session_expiry = datetime.now() + timedelta(hours=1)  # Set session expiry to 1 hour from now

    def clear_session(self):
        self.session_token = None
        self.session_expiry = None