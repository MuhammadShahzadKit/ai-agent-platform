from sqlalchemy import Column, Integer, String

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), unique=True, nullable=False)

    email = Column(String(255), unique=True, nullable=False)

    full_name = Column(String(255), nullable=True)

    password_hash = Column(String(255), nullable=False)