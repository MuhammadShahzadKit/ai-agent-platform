from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    user_message = Column(
        Text,
        nullable=False,
    )

    ai_response = Column(
        Text,
        nullable=False,
    )

    agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=False,
    )

    agent = relationship(
        "Agent",
        back_populates="conversations",
    )