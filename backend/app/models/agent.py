from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.session import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    role = Column(
        String(100),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    system_prompt = Column(
        Text,
        nullable=False,
    )

    model = Column(
        String(100),
        default="qwen2.5:3b",
        nullable=False,
    )

    temperature = Column(
        Integer,
        default=1,
        nullable=False,
    )

    use_rag = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    owner = relationship(
        "User",
        back_populates="agents",
    )

    conversations = relationship(
        "Conversation",
        back_populates="agent",
        cascade="all, delete-orphan",
    )

    missions = relationship(
        "Mission",
        back_populates="agent",
        cascade="all, delete-orphan",
    )