from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.screenshot import Screenshot
from app.schemas.screenshot import ScreenshotCreate, ScreenshotUpdate, ScreenshotResponse
from typing import List, Optional
import hashlib
import uuid


class ScreenshotService:
    def __init__(self, db: Session):
        self.db = db

    def create_screenshot(
        self, 
        screenshot_data: ScreenshotCreate, 
        employee_id: str, 
        organization_id: str
    ) -> Screenshot:
        """Create a new screenshot record"""
        db_screenshot = Screenshot(
            site=screenshot_data.site,
            productivity=screenshot_data.productivity,
            timestamp=screenshot_data.timestamp,
            employeeId=employee_id,
            organizationId=organization_id,
            projectId=screenshot_data.projectId,
            taskId=screenshot_data.taskId,
            shiftId=screenshot_data.shiftId,
            systemPermissions=screenshot_data.systemPermissions or {
                "accessibility": "undetermined",
                "screenAndSystemAudioRecording": "undetermined"
            },
            imageUrl=screenshot_data.imageUrl
        )
        
        self.db.add(db_screenshot)
        self.db.commit()
        self.db.refresh(db_screenshot)
        return db_screenshot

    def get_screenshot(self, screenshot_id: str) -> Optional[Screenshot]:
        """Get screenshot by ID"""
        return self.db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()

    def get_screenshots(
        self,
        organization_id: str,
        start_time: int,
        end_time: int,
        employee_id: str = None,
        team_id: str = None,
        project_id: str = None,
        task_id: str = None,
        shift_id: str = None,
        limit: int = 15,
        next_token: str = None
    ) -> List[Screenshot]:
        """Get screenshots with filters"""
        query = self.db.query(Screenshot).filter(
            and_(
                Screenshot.organizationId == organization_id,
                Screenshot.timestamp >= start_time,
                Screenshot.timestamp <= end_time
            )
        )
        
        if employee_id:
            query = query.filter(Screenshot.employeeId == employee_id)
        
        if team_id:
            query = query.filter(Screenshot.teamId == team_id)
        
        if project_id:
            query = query.filter(Screenshot.projectId == project_id)
        
        if task_id:
            query = query.filter(Screenshot.taskId == task_id)
        
        if shift_id:
            query = query.filter(Screenshot.shiftId == shift_id)
        
        # Handle pagination with next token
        if next_token:
            # Decode next token to get the last screenshot ID
            try:
                last_id = next_token
                query = query.filter(Screenshot.id > last_id)
            except:
                pass  # Invalid token, ignore
        
        screenshots = query.order_by(Screenshot.timestamp.desc()).limit(limit).all()
        return screenshots

    def get_screenshots_paginated(
        self,
        organization_id: str,
        start_time: int,
        end_time: int,
        employee_id: str = None,
        team_id: str = None,
        project_id: str = None,
        task_id: str = None,
        shift_id: str = None,
        limit: int = 10000,
        next_token: str = None,
        sort_by: str = "timestamp"
    ) -> ScreenshotResponse:
        """Get screenshots with pagination"""
        screenshots = self.get_screenshots(
            organization_id=organization_id,
            start_time=start_time,
            end_time=end_time,
            employee_id=employee_id,
            team_id=team_id,
            project_id=project_id,
            task_id=task_id,
            shift_id=shift_id,
            limit=limit + 1,  # Get one extra to check if there are more
            next_token=next_token
        )
        
        # Check if there are more results
        has_more = len(screenshots) > limit
        if has_more:
            screenshots = screenshots[:limit]
        
        # Generate next token
        next_token = None
        if has_more and screenshots:
            # Use the last screenshot ID as the next token
            next_token = screenshots[-1].id
        
        # Get total count (for the current filters, not paginated)
        total_query = self.db.query(Screenshot).filter(
            and_(
                Screenshot.organizationId == organization_id,
                Screenshot.timestamp >= start_time,
                Screenshot.timestamp <= end_time
            )
        )
        
        if employee_id:
            total_query = total_query.filter(Screenshot.employeeId == employee_id)
        if team_id:
            total_query = total_query.filter(Screenshot.teamId == team_id)
        if project_id:
            total_query = total_query.filter(Screenshot.projectId == project_id)
        if task_id:
            total_query = total_query.filter(Screenshot.taskId == task_id)
        if shift_id:
            total_query = total_query.filter(Screenshot.shiftId == shift_id)
        
        total = total_query.count()
        
        return ScreenshotResponse(
            data=screenshots,
            next=next_token,
            total=total
        )

    def update_screenshot(self, screenshot_id: str, screenshot_data: ScreenshotUpdate) -> Optional[Screenshot]:
        """Update screenshot"""
        db_screenshot = self.get_screenshot(screenshot_id)
        if not db_screenshot:
            return None
        
        update_data = screenshot_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_screenshot, field, value)
        
        self.db.commit()
        self.db.refresh(db_screenshot)
        return db_screenshot

    def delete_screenshot(self, screenshot_id: str) -> Optional[Screenshot]:
        """Delete screenshot"""
        db_screenshot = self.get_screenshot(screenshot_id)
        if not db_screenshot:
            return None
        
        self.db.delete(db_screenshot)
        self.db.commit()
        return db_screenshot