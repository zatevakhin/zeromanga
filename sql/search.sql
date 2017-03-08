
SELECT title FROM manga
  WHERE id IN (
    SELECT manga_id FROM manga_genres
    WHERE
        genre_id IN (:gi)
    GROUP BY manga_id
    HAVING COUNT(*) == :gic
  ) AND id IN (
    SELECT manga_id FROM manga_genres
    WHERE
        NOT genre_id IN (:ge)
    GROUP BY manga_id
  )
LIMIT 100;