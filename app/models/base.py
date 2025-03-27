from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum
from app.core.database import Base
from datetime import datetime
import enum
import uuid

class UserRole(str , enum.Enum):
    RECRUITER = "recruiter"
    ADMIN = "admin"
    INTERVIEWER = "interviewer"
    CANDIDATE = "candidate"

    def __str__(self):
        return self.value
    
    @property
    def name(self):
        return self.value
  
# Add this new User class to your existing models file
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, nullable=False) 
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # For interviewers to track which interviews they're assigned to
    interviews_assigned = relationship("Interview", back_populates="interviewer_user")

class JobPosting(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    department = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(Text, nullable=False)
    employment_type = Column(String, nullable=False)

    candidates = relationship("Candidate", back_populates="job")
    interviews = relationship("Interview", back_populates="job")

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    cv_text = Column(Text, nullable=False)
    status = Column(String, nullable=False)  # Applied, Screening, etc.
    job_id = Column(Integer, ForeignKey('jobs.id'))

    job = relationship("JobPosting", back_populates="candidates")
    interviews = relationship("Interview", back_populates="candidate")
    notifications = relationship("Notification", back_populates="candidate")

class Interview(Base):
    __tablename__ = "interviews"
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    job_id = Column(Integer, ForeignKey('jobs.id') , nullable=True)
    interviewer_name = Column(String, nullable=False)  # Keep this for backward compatibility
    interviewer_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # New field
    scheduled_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    completed = Column(Boolean, default=False)
    
    candidate = relationship("Candidate", back_populates="interviews")
    job = relationship("JobPosting", back_populates="interviews")
    feedback = relationship("Feedback", back_populates="interview", uselist=False)
    interviewer_user = relationship("User", back_populates="interviews_assigned")
    @property
    def interviewer(self):
        return self.interviewer_name
class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    interview_id = Column(Integer, ForeignKey('interviews.id'), unique=True)
    comments = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 rating
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    recommendation = Column(String, nullable=True)  # Hire, Reject, Another Interview
    created_at = Column(DateTime, default=datetime.utcnow)
    
    interview = relationship("Interview", back_populates="feedback")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # status_change, interview_scheduled, feedback_added
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    candidate = relationship("Candidate", back_populates="notifications")