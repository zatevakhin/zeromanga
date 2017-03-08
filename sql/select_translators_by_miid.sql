SELECT
  translators.value
FROM translators
  JOIN manga_translators ON translators.id = manga_translators.translator_id
WHERE manga_id = :miid