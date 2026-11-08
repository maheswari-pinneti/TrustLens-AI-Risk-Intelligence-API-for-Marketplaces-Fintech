"""
Merchant Database Repository
"""
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database.models import Merchant


class MerchantRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_merchant_id(self, merchant_id: str) -> Optional[Merchant]:
        return self.db.query(Merchant).filter(Merchant.merchant_id == merchant_id).first()

    def create_or_update(self, data: Dict[str, Any]) -> Merchant:
        merchant_id = data.get("merchant_id")
        merchant = self.get_by_merchant_id(merchant_id)
        if not merchant:
            merchant = Merchant(**data)
            self.db.add(merchant)
        else:
            for k, v in data.items():
                setattr(merchant, k, v)
        self.db.commit()
        self.db.refresh(merchant)
        return merchant

    def list_merchants(
        self,
        skip: int = 0,
        limit: int = 50,
        risk_level: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Merchant], int]:
        query = self.db.query(Merchant)
        if risk_level:
            query = query.filter(Merchant.risk_level.ilike(risk_level))
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                (Merchant.name.ilike(pattern)) |
                (Merchant.merchant_id.ilike(pattern)) |
                (Merchant.email.ilike(pattern))
            )
        total = query.count()
        items = query.order_by(desc(Merchant.risk_score)).offset(skip).limit(limit).all()
        return items, total

    def count(self) -> int:
        return self.db.query(func.count(Merchant.id)).scalar() or 0
