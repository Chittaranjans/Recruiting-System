from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class InterviewBase(BaseModel):
    candidate_id: int
    job_id: Optional[int] =None
    interviewer: str
    scheduled_date: datetime
    duration_minutes: int = 60
    completed: bool = False

class InterviewCreate(InterviewBase):
    pass

class Interview(InterviewBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class FeedbackBase(BaseModel):
    interview_id: int
    comments: str
    rating: int
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recommendation: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class InterviewWithFeedback(Interview):
    feedback: Optional[Feedback] = None
    model_config = ConfigDict(from_attributes=True)