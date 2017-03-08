SELECT
  us.login,
  uq.uhash,
  uq.uiid,
  uq.url
FROM
  upload_queue AS uq JOIN users AS us ON uq.uiid = us.id
ORDER BY stamp DESC

LIMIT 100
