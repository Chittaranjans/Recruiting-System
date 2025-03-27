import datetime
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "candidate"  # Default to candidate, but can be overridden

class User(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    is_approved: bool = False
    created_at: datetime

    class Config:
        orm_mode = True