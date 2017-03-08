INSERT OR REPLACE INTO chapters (
  id, mangaid, chash, chapter, pages, `index`
) VALUES (
  (SELECT id FROM chapters WHERE chash = :chash), :mangaid, :chash, :chapter, :pages, :index
)