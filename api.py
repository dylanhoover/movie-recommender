from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from recommender import get_content_based_recommendations_fuzzy
from movie_info import get_movie_info
from fastapi.responses import Response
from database import get_db
from sqlalchemy.orm import Session
import numpy as np

app = FastAPI(title="Movie Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendationRequest(BaseModel):
    title: str
    num_recommendations: int = 10


class RecommendationResponse(BaseModel):
    recommendations: list[dict]


class MovieDetailResponse(BaseModel):
    id: int
    title: str
    # genres: list[str]
    # overview: str
    # release_date: str
    # runtime: int
    # vote_average: float
    # vote_count: int


@app.get("/recommend/{title}/{num_recommendations}", response_model=RecommendationResponse)
def recommend_movies(title: str, num_recommendations: int):
    try:
        recommendations = get_content_based_recommendations_fuzzy(
            title, num_recommendations)
        for recommendation in recommendations:
            for key, value in recommendation.items():
                if isinstance(value, np.int64):
                    recommendation[key] = int(value)
        return RecommendationResponse(recommendations=recommendations)
    except KeyError:
        raise HTTPException(status_code=404, detail="Movie title not found")


@app.get("/movie/{movie_id}")
def get_movie_details_endpoint(movie_id: int, db: Session = Depends(get_db)):
    # try:
    details = get_movie_info(movie_id)
    return details
    # return Response(content=details, media_type="application/json")
    # except ValueError as ve:
    #     raise HTTPException(status_code=404, detail=str(ve))
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500, detail="An unexpected error occurred.")
