from database import Base
from sqlalchemy import Column , Integer ,String ,Boolean, Float

class Movies(Base):

    __tablename__ = 'movietable'

    movie_id =Column(Integer ,primary_key = True , index=True)
    title = Column(String)
    director = Column (String)
    genre = Column(String)
    duration = Column (Integer)
    rating = Column (Float)