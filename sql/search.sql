SELECT *, (manga.name || manga.english || manga.original) AS search FROM manga
  WHERE id IN (
    SELECT manga_id FROM manga_genres WHERE genre_id IN ({})
  ) AND id NOT IN (
    SELECT manga_id FROM manga_genres WHERE genre_id IN ({})
  ) LIMIT 100;
