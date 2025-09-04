CREATE TABLE IF NOT EXISTS spec_genre_ratings AS
SELECT
    g.genre_name,
    AVG(m.vote_average) as average_rating,
    COUNT(m.movie_id) as movie_count
FROM
    sot_movies_clean m
        JOIN
    sot_movie_genres g ON m.movie_id = g.movie_id
GROUP BY
    g.genre_name
ORDER BY
    average_rating DESC;