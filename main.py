from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Annotated, Literal

import models
from models import Movies
from database import engine, SessionLocal

app = FastAPI()

# Allowed genres
Genre = Literal["action", "comedy", "drama", "thriller"]


# Pydantic model for creating a movie
class MovieCreate(BaseModel):
    movie_id: int = Field(gt=0, lt=100)
    title: str
    director: str
    genre: Genre
    duration: int = Field(gt=0)
    rating: float = Field(ge=0, le=5)


# Pydantic model for updating a movie
class MovieUpdate(BaseModel):
    title: str
    director: str
    genre: Genre
    duration: int = Field(gt=0)
    rating: float = Field(ge=0, le=5)


# Create database tables
models.Base.metadata.create_all(bind=engine)


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# 1. GET /movies/sort

@app.get("/movies/sort")
def sort_movies(db: db_dependency,sort_by: Literal["duration", "rating"] = "rating",order: Literal["asc", "desc"] = "desc"):
    sort_column = getattr(Movies, sort_by)

    if order == "asc":
        return db.query(Movies).order_by(sort_column.asc()).all()

    return db.query(Movies).order_by(sort_column.desc()).all()


# 2. GET /movies
@app.get("/movies")
def view_movies(db: db_dependency):
    return db.query(Movies).all()


# 3. GET /movies/{movie_id}
@app.get("/movies/{movie_id}")
def view_specific_movie(db: db_dependency, movie_id: int):
    movie = (db.query(Movies).filter(Movies.movie_id == movie_id).first())

    if movie is None:
        raise HTTPException(status_code=404,detail="Movie not found")

    return movie


# 4. POST /create_movies
@app.post("/create_movies", status_code=201)
def create_movie(db: db_dependency, new_movie: MovieCreate):
    existing_movie = (db.query(Movies).filter(Movies.movie_id == new_movie.movie_id).first())

    if existing_movie is not None:
        raise HTTPException(status_code=400,detail="Movie with this ID already exists")

    movie_model = Movies(**new_movie.model_dump())

    db.add(movie_model)
    db.commit()
    db.refresh(movie_model)

    return movie_model


# 5. PUT /movies/{movie_id}
@app.put("/movies/{movie_id}")
def update_movie(db: db_dependency,movie_id: int,update_movie: MovieUpdate):
    movie = (db.query(Movies).filter(Movies.movie_id == movie_id).first())

    if movie is None:
        raise HTTPException(status_code=404,detail="Movie not found")

    update_data = update_movie.model_dump()

    for key, value in update_data.items():
        setattr(movie, key, value)

    db.commit()
    db.refresh(movie)

    return movie


# 6. DELETE /movies/{movie_id}
@app.delete("/movies/{movie_id}")
def delete_movie(db: db_dependency, movie_id: int):
    movie = (db.query(Movies).filter(Movies.movie_id == movie_id).first())

    if movie is None:
        raise HTTPException(status_code=404,detail="Movie not found")

    db.delete(movie)
    db.commit()

    return {"message": "Movie deleted successfully"}
