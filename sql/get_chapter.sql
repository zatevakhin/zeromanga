SELECT chapters.*, manga.path as path FROM chapters
  JOIN manga ON chapters.mangaid = manga.id
WHERE
  mhash = :mhash AND
  chash = :chash
LIMIT 1
