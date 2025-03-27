from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.core.database import get_db

router = APIRouter()

@router.get("/notifications/", response_model=List[schemas.Notification])
def get_notifications(
    db: Session = Depends(get_db),
    candidate_id: int = None,
    unread_only: bool = False
):
    """Get notifications with optional filtering"""
    query = db.query(models.Notification)
    
    if candidate_id:
        query = query.filter(models.Notification.candidate_id == candidate_id)
    
    if unread_only:
        query = query.filter(models.Notification.is_read == False)
    
    # Order by most recent
    query = query.order_by(models.Notification.created_at.desc())
    
    notifications = query.all()
    return notifications

@router.put("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    """Mark a notification as read"""
    notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    
    return {"id": notification.id, "is_read": True}

@router.put("/notifications/read-all")
def mark_all_notifications_read(candidate_id: int, db: Session = Depends(get_db)):
    """Mark all notifications for a candidate as read"""
    notifications = db.query(models.Notification).filter(
        models.Notification.candidate_id == candidate_id,
        models.Notification.is_read == False
    ).all()
    
    if not notifications:
        return {"message": "No unread notifications found"}
    
    count = 0
    for notification in notifications:
        notification.is_read = True
        count += 1
    
    db.commit()
    
    return {"message": f"{count} notifications marked as read"}