INSERT OR REPLACE INTO chapters (
  id, mangaid, chash, chapter, pages, `index`
) VALUES (
  (SELECT id FROM chapters WHERE chash = :chash),
  (SELECT id FROM manga WHERE mhash = :uhash),
  :chash, :chapter, :pages, :index
)