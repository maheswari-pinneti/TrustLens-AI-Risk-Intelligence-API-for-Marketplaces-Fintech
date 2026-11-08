"""
User Database Repository
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.database.models import User
from app.security.authentication import hash_password, generate_api_key


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_api_key(self, api_key: str) -> Optional[User]:
        return self.db.query(User).filter(User.api_key == api_key).first()

    def create(self, username: str, email: str, password: str, role: str = "analyst") -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=role,
            api_key=generate_api_key()
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def regenerate_api_key(self, user_id: int) -> Optional[str]:
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.api_key = generate_api_key()
        self.db.commit()
        self.db.refresh(user)
        return user.api_key
