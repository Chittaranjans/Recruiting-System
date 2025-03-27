from pydantic import BaseModel , ConfigDict
from typing import Optional

class JobBase(BaseModel):
    title: str
    department: str
    description: str
    required_skills: str
    employment_type: str

class CandidateBase(BaseModel):
    name: str
    email: str
    cv_text: str
    status: str
    job_id: int


class CandidateCreate(CandidateBase):
    pass

class Candidate(CandidateBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
    
class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
   