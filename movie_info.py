import pandas as pd
import json
from fastapi.responses import Response
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from models import Movie
from database import get_db
df2 = pd.read_csv('tmdb_5000_movies.csv')

required_columns = {'id', 'title', 'genres', 'overview',
                    'release_date', 'runtime', 'vote_average', 'vote_count'}
missing_columns = required_columns - set(df2.columns)

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

movie_details = df2.set_index('id').to_dict(orient='index')


def get_movie_info(movie_id: int):
    return movie_details[movie_id]


# def get_movie_info(movie_id: int, db: Session = Depends(get_db)):
#     movie = db.query(Movie).filter(Movie.id == movie_id).first()
#     if movie is None:
#         raise HTTPException(status_code=404, detail="Movie not found")
#     return movie
