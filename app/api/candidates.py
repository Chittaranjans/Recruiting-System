from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.core.database import get_db
from app.core.auth import get_current_user, is_recruiter_or_admin, is_interviewer_or_above

router = APIRouter()

@router.post("/candidates/", response_model=schemas.Candidate)
def create_candidate(
    candidate: schemas.CandidateCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(is_recruiter_or_admin)  # Only recruiters/admins can add candidates
):
    # Check if job exists
    job = db.query(models.JobPosting).filter(models.JobPosting.id == candidate.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    try:
        db_candidate = models.Candidate(
            name=candidate.name,
            email=candidate.email,
            cv_text=candidate.cv_text,
            status=candidate.status,
            job_id=candidate.job_id
        )
        
        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate)
        return db_candidate
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/candidates/", response_model=List[schemas.Candidate])
def read_candidates(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(is_interviewer_or_above)  # Interviewers and above can view candidates
):
    candidates = db.query(models.Candidate).offset(skip).limit(limit).all()
    return candidates

@router.get("/candidates/{candidate_id}", response_model=schemas.Candidate)
def read_candidate(
    candidate_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(is_interviewer_or_above)  # Interviewers and above can view candidates
):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.put("/candidates/{candidate_id}", response_model=schemas.Candidate)
def update_candidate(
    candidate_id: int, 
    candidate: schemas.CandidateCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(is_recruiter_or_admin)  # Only recruiters/admins can update candidates
):
    db_candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not db_candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Check if job exists
    if candidate.job_id:
        job = db.query(models.JobPosting).filter(models.JobPosting.id == candidate.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
    
    for key, value in vars(candidate).items():
        setattr(db_candidate, key, value)
    
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

@router.delete("/candidates/{candidate_id}")
def delete_candidate(
    candidate_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(is_recruiter_or_admin)  # Only recruiters/admins can delete candidates
):
    db_candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not db_candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    db.delete(db_candidate)
    db.commit()
    return {"detail": "Candidate deleted successfully"}

@router.post("/candidates/upload/")
async def upload_cv(
    name: str = Form(...),
    email: str = Form(...),
    job_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check if job exists
    job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Read file contents
    cv_content = await file.read()
    try:
        cv_text = cv_content.decode("utf-8")
    except UnicodeDecodeError:
        cv_text = f"Binary content from {file.filename}"
    
    # Create candidate with uploaded CV
    db_candidate = models.Candidate(
        name=name,
        email=email,
        cv_text=cv_text,
        status="Applied",  # Initial status
        job_id=job_id
    )
    
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    
    return db_candidate

@router.put("/candidates/{candidate_id}/status")
def update_status(
    candidate_id: int, 
    status: str,
    db: Session = Depends(get_db)
):
    db_candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not db_candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    valid_statuses = ["Applied", "Screening", "Interview Scheduled", "Offer Extended", "Rejected", "Hired"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    db_candidate.status = status
    db.commit()
    db.refresh(db_candidate)
    
    return {"id": db_candidate.id, "status": db_candidate.status}

@router.get("/jobs/{job_id}/candidates", response_model=List[schemas.Candidate])
def get_candidates_for_job(job_id: int, db: Session = Depends(get_db)):
    # Check if job exists
    job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get all candidates for this job
    candidates = db.query(models.Candidate).filter(models.Candidate.job_id == job_id).all()
    return candidates

# Uncomment this if you want to implement CV summarization with OpenAI
# @router.post("/candidates/{candidate_id}/summarize")
# async def summarize_cv(candidate_id: int, db: Session = Depends(get_db)):
#     candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
#     if not candidate:
#         raise HTTPException(status_code=404, detail="Candidate not found")
#     
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": f"Summarize this CV:\n{candidate.cv_text}"}]
#     )
#     
#     return {"summary": response.choices[0].message.content}