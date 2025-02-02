from pydantic import BaseModel, EmailStr

class RegistrationCreate(BaseModel):
    full_name: str
    whatsapp_number: str
    email: EmailStr
    gender: str
    preferred_course: str
    agreement: bool

class UserCreate(BaseModel):
    username: str
    fullname: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    fullname: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    session_token: str = None
    reset_token: str = None

    class Config:
        from_attribute = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str