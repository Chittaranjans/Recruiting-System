from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.core.database import get_db
from app.core.auth import get_current_user, is_recruiter_or_admin
from typing import List

router = APIRouter()

@router.post("/jobs/", response_model=schemas.Job)
def create_job(
    job: schemas.JobCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(is_recruiter_or_admin)  # Only recruiters/admins can create jobs
):
    print(f"Type of job: {type(job)}")
    print(f"Job data: {job}")
    print(f"Creating job as user: {current_user.username}, role: {current_user.role}")

    try:
        # Create JobPosting with data from the job parameter
        db_job = models.JobPosting(
            title=job.title,
            department=job.department,
            description=job.description,
            required_skills=job.required_skills,
            employment_type=job.employment_type
        )
        
        try:
            db.add(db_job)
            print("Job added to session")
            db.commit()
            print("Session committed")
            db.refresh(db_job)
            print(f"Job refreshed, id: {db_job.id}")
            
            # Convert to dict for debugging
            job_dict = {
                "id": db_job.id,
                "title": db_job.title,
                "department": db_job.department,
                "description": db_job.description,
                "required_skills": db_job.required_skills,
                "employment_type": db_job.employment_type
            }
            print(f"Job as dict: {job_dict}")
            
            return db_job
            
        except Exception as db_err:
            print(f"Database operation error: {str(db_err)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_err)}")
            
    except Exception as e:
        print(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/jobs/", response_model=List[schemas.Job])
def get_jobs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)  # All users can view jobs
):
    jobs = db.query(models.JobPosting).offset(skip).limit(limit).all()
    return jobs

@router.get("/jobs/{job_id}", response_model=schemas.Job)
def read_job(
    job_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)  # All users can view job details
):
    job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/jobs/{job_id}", response_model=schemas.Job)
def update_job(
    job_id: int, 
    job: schemas.JobCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(is_recruiter_or_admin)  # Only recruiters/admins can update jobs
):
    db_job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    for key, value in job.dict().items():
        setattr(db_job, key, value)
    db.commit()
    db.refresh(db_job)
    return db_job

@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(is_recruiter_or_admin)  # Only recruiters/admins can delete jobs
):
    db_job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(db_job)
    db.commit()
    return {"detail": "Job deleted successfully"}

# Similar CRUD endpoints for candidates, interviews
