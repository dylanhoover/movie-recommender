from sqlalchemy import Column, Integer, String, Float
from database import Base


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    genres = Column(String)
    # Add other fields as necessary
