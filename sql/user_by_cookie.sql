SELECT u.* FROM
  users AS u JOIN authorized AS a ON u.id = a.uiid
WHERE
  a.cookie == :cookie
LIMIT 1