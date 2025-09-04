CREATE TABLE IF NOT EXISTS sot_movies_clean (
                                                movie_id INTEGER PRIMARY KEY,
                                                title TEXT,
                                                vote_average REAL
);

CREATE TABLE IF NOT EXISTS sot_movie_genres (
                                                movie_id INTEGER,
                                                genre_name TEXT,
                                                PRIMARY KEY (movie_id, genre_name)
    );