from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from .job import Candidate

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "candidate"  # Default role

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    username: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
    role: str
    exp: Optional[datetime] = None