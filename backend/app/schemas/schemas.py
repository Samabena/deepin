from pydantic import BaseModel, EmailStr

class RegistrationCreate(BaseModel):
    full_name: str
    whatsapp_number: str
    email: EmailStr
    gender: str
    preferred_course: str
    agreement: bool
