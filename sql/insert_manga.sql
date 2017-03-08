INSERT OR REPLACE INTO manga (

  id, mhash, url, title, path, description, covers, year, volumes, chapters, mature, single, translation, state, rating

) VALUES (
  (SELECT id FROM manga WHERE mhash = :hash),
  :hash,
  :url,
  :title,
  :path,
  :description,
  :covers,
  :year,
  :volumes,
  :chapters,
  :mature,
  :single,
  :translation,
  :state,
  :rating
)
