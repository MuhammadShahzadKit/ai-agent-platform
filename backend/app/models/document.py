from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)

    vector_db = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")