SELECT c.*, m.resource AS resource FROM
  chapters AS c JOIN
  manga AS m ON c.mangaid = m.id
WHERE
  mhash = :mhash AND
  chash = :chash
LIMIT 1
