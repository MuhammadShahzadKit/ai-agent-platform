from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)

    objective = Column(Text, nullable=False)

    status = Column(
        String(50),
        default="pending",
    )

    result = Column(
        Text,
        nullable=True,
    )

    agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
    )

    agent = relationship(
        "Agent",
        back_populates="missions",
    )