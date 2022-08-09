from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hash_password = Column(String)
    is_active = Column(Boolean, default=True)

    quotes = relationship("Quotes", back_populates="owner")


class Quotes(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    movie = Column(String) ## title
    movie_character = Column(String)
    quote = Column(String)
    rating = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("Users", back_populates="quotes")
