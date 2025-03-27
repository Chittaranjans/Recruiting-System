from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from app import models, schemas
from app.core.database import get_db

router = APIRouter()

@router.get("/kanban", response_model=Dict[str, List[schemas.Candidate]])
def get_kanban_board(db: Session = Depends(get_db)):
    """
    Get candidates grouped by their recruitment status (Kanban board view)
    """
    # Get all valid statuses
    valid_statuses = ["Applied", "Screening", "Interview Scheduled", "Offer Extended", "Rejected", "Hired"]
    
    # Initialize result dictionary
    result = {status: [] for status in valid_statuses}
    
    # Query all candidates
    candidates = db.query(models.Candidate).all()
    
    # Group candidates by status
    for candidate in candidates:
        if candidate.status in result:
            result[candidate.status].append(candidate)
    
    return result

@router.put("/kanban/move")
def move_candidate_status(
    candidate_id: int,
    new_status: str,
    db: Session = Depends(get_db)
):
    """
    Move a candidate from one status to another (for drag-and-drop functionality)
    """
    # Verify the candidate exists
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Verify the status is valid
    valid_statuses = ["Applied", "Screening", "Interview Scheduled", "Offer Extended", "Rejected", "Hired"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    # Update status
    old_status = candidate.status
    candidate.status = new_status
    
    # Create notification for status change
    notification = models.Notification(
        candidate_id=candidate_id,
        message=f"Candidate status changed from {old_status} to {new_status}",
        type="status_change"
    )
    db.add(notification)
    
    db.commit()
    
    return {"id": candidate.id, "old_status": old_status, "new_status": new_status}