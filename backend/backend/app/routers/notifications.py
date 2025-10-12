from typing import List

from app import database, models, schemas
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/", response_model=List[schemas.NotificationOut])
def get_notifications(user_id: int, db: Session = Depends(database.get_db)):
    try:
        notifications = db.query(models.Notification).filter(
            models.Notification.user_id == user_id
        ).order_by(models.Notification.created_at.desc()).limit(20).all()
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")

@router.get("/unread-count")
def get_unread_count(user_id: int, db: Session = Depends(database.get_db)):
    try:
        count = db.query(models.Notification).filter(
            models.Notification.user_id == user_id,
            models.Notification.is_read == False
        ).count()
        return {"unread_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error counting unread notifications: {str(e)}")

@router.post("/mark-read/{notification_id}")
def mark_as_read(notification_id: int, db: Session = Depends(database.get_db)):
    try:
        notification = db.query(models.Notification).filter(
            models.Notification.id == notification_id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.is_read = True
        db.commit()
        return {"message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notification as read: {str(e)}")

@router.post("/mark-all-read")
def mark_all_as_read(user_id: int, db: Session = Depends(database.get_db)):
    try:
        db.query(models.Notification).filter(
            models.Notification.user_id == user_id,
            models.Notification.is_read == False
        ).update({"is_read": True})
        db.commit()
        return {"message": "All notifications marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking all notifications as read: {str(e)}")

@router.delete("/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(database.get_db)):
    try:
        notification = db.query(models.Notification).filter(
            models.Notification.id == notification_id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        db.delete(notification)
        db.commit()
        return {"message": "Notification deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notification: {str(e)}")