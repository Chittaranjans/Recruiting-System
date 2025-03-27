from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.core.database import get_db
from app.core.auth import get_current_user, is_recruiter_or_admin, is_interviewer_or_above
from datetime import datetime

router = APIRouter()

@router.post("/interviews/", response_model=schemas.Interview)
def create_interview(
    interview: schemas.InterviewCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(is_recruiter_or_admin)  # Only recruiters/admins can schedule interviews
):
    """Schedule a new interview"""
    # Verify candidate exists
    candidate = db.query(models.Candidate).filter(models.Candidate.id == interview.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Verify job exists
    job = db.query(models.JobPosting).filter(models.JobPosting.id == interview.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    try:
        # Create new interview
        db_interview = models.Interview(
            candidate_id=interview.candidate_id,
            job_id=interview.job_id,
            interviewer_name=interview.interviewer,  # Keep for backward compatibility
            interviewer_user_id=current_user.id,  # Link to the user who scheduled it
            scheduled_date=interview.scheduled_date,
            duration_minutes=interview.duration_minutes,
            completed=interview.completed
        )
        
        db.add(db_interview)
        
        # Update candidate status if currently in "Applied" or "Screening"
        if candidate.status in ["Applied", "Screening"]:
            candidate.status = "Interview Scheduled"
            
        # Create notification
        notification = models.Notification(
            candidate_id=interview.candidate_id,
            message=f"Interview scheduled with {interview.interviewer} on {interview.scheduled_date.strftime('%Y-%m-%d %H:%M')}",
            type="interview_scheduled"
        )
        db.add(notification)
            
        db.commit()
        db.refresh(db_interview)
        return db_interview
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating interview: {str(e)}")

@router.get("/interviews/", response_model=List[schemas.InterviewWithFeedback])
def get_interviews(
    db: Session = Depends(get_db), 
    candidate_id: int = None, 
    job_id: int = None,
    current_user: schemas.User = Depends(get_current_user)  # All authenticated users can view interviews
):
    """Get all interviews with optional filtering"""
    query = db.query(models.Interview)
    
    # For interviewers, only show interviews they're assigned to
    if current_user.role == "interviewer":
        query = query.filter(models.Interview.interviewer_user_id == current_user.id)
    
    if candidate_id:
        query = query.filter(models.Interview.candidate_id == candidate_id)
    
    if job_id:
        query = query.filter(models.Interview.job_id == job_id)
    
    interviews = query.all()
    return interviews

@router.get("/interviews/{interview_id}", response_model=schemas.InterviewWithFeedback)
def get_interview(
    interview_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)  # All authenticated users
):
    """Get a specific interview by ID"""
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Check permissions
    if current_user.role == "interviewer" and interview.interviewer_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to view this interview")
    
    return interview

@router.post("/feedback/", response_model=schemas.Feedback)
def add_feedback(
    feedback: schemas.FeedbackCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(is_interviewer_or_above)  # Interviewers and above can add feedback
):
    """Add feedback for an interview"""
    # Verify interview exists
    interview = db.query(models.Interview).filter(models.Interview.id == feedback.interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Check if user is allowed to add feedback (must be the interviewer or an admin/recruiter)
    if current_user.role == "interviewer" and interview.interviewer_user_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You can only provide feedback for interviews you're assigned to"
        )
    
    # Check if feedback already exists
    existing_feedback = db.query(models.Feedback).filter(
        models.Feedback.interview_id == feedback.interview_id
    ).first()
    
    if existing_feedback:
        raise HTTPException(status_code=400, detail="Feedback already exists for this interview")
    
    try:
        # Create feedback
        db_feedback = models.Feedback(
            interview_id=feedback.interview_id,
            comments=feedback.comments,
            rating=feedback.rating,
            strengths=feedback.strengths,
            weaknesses=feedback.weaknesses,
            recommendation=feedback.recommendation
        )
        
        db.add(db_feedback)
        
        # Mark interview as completed
        interview.completed = True
        
        # Create notification
        notification = models.Notification(
            candidate_id=interview.candidate_id,
            message=f"Feedback added for your interview with {interview.interviewer_name}",
            type="feedback_added"
        )
        db.add(notification)
        
        db.commit()
        db.refresh(db_feedback)
        return db_feedback
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding feedback: {str(e)}")