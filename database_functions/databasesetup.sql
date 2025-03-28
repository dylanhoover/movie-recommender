-- Create a table for movies
CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genres TEXT
);

-- Create a table for ratings
CREATE TABLE ratings (
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    rating FLOAT NOT NULL,
    timestamp BIGINT NOT NULL,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);

-- Create a table for credits
CREATE TABLE credits (
    movie_id INT PRIMARY KEY,
    title VARCHAR(255),
    cast JSONB,
    crew JSONB,
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);

-- Import data into the movies table
COPY movies(id, title, genres) FROM '/path/to/movies.csv' DELIMITER ',' CSV HEADER;

-- Import data into the ratings table
COPY ratings(user_id, movie_id, rating, timestamp) FROM '/path/to/ratings.csv' DELIMITER ',' CSV HEADER;

-- Import data into the credits table
COPY credits(movie_id, title, cast, crew) FROM '/path/to/tmdb_5000_credits.csv' DELIMITER ',' CSV HEADER;