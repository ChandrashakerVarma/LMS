from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, LargeBinary, DateTime, String
from sqlalchemy.orm import relationship

from app.database import Base


class UserFace(Base):
    __tablename__ = "user_faces"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, unique=True)

    embedding = Column(LargeBinary, nullable=False)
    model_name = Column(String(100), default="face_recognition_resnet")

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="faces")
