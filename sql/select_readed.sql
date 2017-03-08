SELECT
  uread.pageid
FROM uread
  JOIN users ON uread.userid = users.id
  JOIN manga ON uread.mangaid = manga.id
  JOIN chapters ON uread.chaptid = chapters.id
WHERE
  uread.userid  = :uiid AND
  uread.mangaid = :miid AND
  uread.chaptid = :ciid
