# https://www.kaggle.com/code/ibtesama/getting-started-with-a-movie-recommendation-system

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process, fuzz

df1 = pd.read_csv('tmdb_5000_credits.csv')
df2 = pd.read_csv('tmdb_5000_movies.csv')

df1.columns = ['id', 'tittle', 'cast', 'crew']
df2 = df2.merge(df1, on='id')


# print(df2.head())

C = df2['vote_average'].mean()
m = df2['vote_count'].quantile(0.9)

q_movies = df2.copy().loc[df2['vote_count'] >= m]


def weighted_rating(x, m=m, C=C):
    v = x['vote_count']
    R = x['vote_average']
    # Calculation based on the IMDB formula
    return (v/(v+m) * R) + (m/(m+v) * C)


# Define a new feature 'score' and calculate its value with `weighted_rating()`
q_movies['score'] = q_movies.apply(weighted_rating, axis=1)

# Sort movies based on score calculated above
q_movies = q_movies.sort_values('score', ascending=False)
# print(q_movies.head())
# print(q_movies.columns)

# Print the top 15 movies
# print(q_movies[['title_y', 'vote_count', 'vote_average', 'score']].head(15))


tfidf = TfidfVectorizer(stop_words='english')

df2['overview'] = df2['overview'].fillna('')

tfidf_matrix = tfidf.fit_transform(df2['overview'])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

indices = pd.Series(df2.index, index=df2['title']).drop_duplicates()


def get_recommendations(title, cosine_sim=cosine_sim):
    # Get the index of the movie that matches the title
    idx = indices[title]

    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[1:11]

    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]

    # Print the columns in df2 before returning recommendations
    # print("Available columns in df2:", df2.columns)

    # Return the top 10 most similar movies as a list of objects
    return [
        {
            'id': df2['id'].iloc[i],
            'title': df2['title'].iloc[i],
            'release_date': df2['release_date'].iloc[i]
        } for i in movie_indices
    ]

# print(get_recommendations('The Dark Knight Rises'))


features = ['cast', 'crew', 'keywords', 'genres']
for feature in features:
    df2[feature] = df2[feature].apply(literal_eval)


def get_director(x):
    for i in x:
        if i['job'] == 'Director':
            return i['name']
    return np.nan


def get_list(x):
    if isinstance(x, list):
        names = [i['name'] for i in x]
        # Check if more than 3 elements exist. If not, return empty string
        if len(names) > 3:
            names = names[:3]
        return names
    return []


df2['director'] = df2['crew'].apply(get_director)


features = ['cast', 'keywords', 'genres']
for feature in features:
    df2[feature] = df2[feature].apply(get_list)

# print(df2[['title', 'cast', 'director', 'keywords', 'genres']].head(3))


def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    else:
        # Check if director exists. If not, return empty string
        if isinstance(x, str):
            return str.lower(x.replace(" ", ""))
        else:
            return ''


features = ['cast', 'keywords', 'director', 'genres']

for feature in features:
    df2[feature] = df2[feature].apply(clean_data)


def create_soup(x):
    return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director'] + ' ' + ' '.join(x['genres'])


df2['soup'] = df2.apply(create_soup, axis=1)

# create the count matrix
count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(df2['soup'])

# compute the cosine similarity matrix
cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

# reset index of our main DataFrame and construct reverse mapping as before
df2 = df2.reset_index()
indices = pd.Series(df2.index, index=df2['title'])

movie_titles = df2['title'].tolist()


def get_closet_title(input_title, threashold=80):
    match = process.extractOne(
        input_title, movie_titles, scorer=fuzz.WRatio)
    print(match)
    if match[1] >= threashold:
        return match[0]
    else:
        return None


# collaborative filtering
# raitings = pd.read_csv('ratings.csv')
# movies = pd.read_csv('movies.csv')
# user_item_matrix = raitings.pivot(index='userId', columns='movieId', values='rating')
# # need to fill NaN with 0
# user_item_matrix = user_item_matrix.fillna(0)

# n_factors = 50
# svd = TruncatedSVD(n_components=n_factors, random_state=42)
# latent_matrix = svd.fit_transform(user_item_matrix)


# def get_collaborative_recommendations(user_id, num_recommendations=10):
#     if user_id not in user_item_matrix.index:
#         print(f"User ID {user_id} not found. Falling back to content-based recommendations.")
#         return []

#     user_idx = user_item_matrix.index.get_loc(user_id)
#     user_latent = latent_matrix[user_idx]

#     #Compute similarity between user latent vector and all latent vectors in the matrix
#     scores = latent_matrix.dot(user_latent)
#     scores_series = pd.Series(scores, index=user_item_matrix.columns)

#     rated_movies = raitings[raitings['userId'] == user_id]['movieId'].tolist()

#     #Exclude rated movies from recommendations
#     scores_series = scores_series.drop(rated_movies)

#     top_movie_ids = scores_series.sort_values(ascending=False).head(num_recommendations).index.tolist()

#     recommended_movies = df2[df2['id'].isin(top_movie_ids)]['title'].tolist()

#     return recommended_movies

# print(get_collaborative_recommendations(1, 10))


def get_content_based_recommendations_fuzzy(title, num_recommendations=10):
    try:
        idx = indices[title]
        matched_title = title
    except KeyError:
        print("KeyError")
        # if title is not in the indices, find the closest match
        closest_title = get_closet_title(title)
        if closest_title:
            matched_title = closest_title
        else:
            raise ValueError(f"No close match found for {title}")

    # pass title to get_recommendations
    recommendations = get_recommendations(matched_title, cosine_sim2)
    return recommendations[:num_recommendations]


# print(get_content_based_recommendations_fuzzy('Incepton', 10))
