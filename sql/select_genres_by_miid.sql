SELECT
  genres.value
FROM genres
  JOIN manga_genres ON genres.id = manga_genres.genre_id
WHERE manga_id = :miid