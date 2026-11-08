"""
Audit Log Repository
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.models import AuditLog


class AuditRepository:

    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        entry = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            username=username,
            details=details or {},
            ip_address=ip_address
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def list_recent(self, limit: int = 50) -> List[AuditLog]:
        return self.db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).all()
