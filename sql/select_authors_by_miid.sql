SELECT
  authors.value
FROM authors
  JOIN manga_authors ON authors.id = manga_authors.author_id
WHERE manga_id = :miid