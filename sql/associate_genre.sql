INSERT OR IGNORE INTO manga_genres (genre_id, manga_id) VALUES (
  (SELECT id FROM genres WHERE value == :genre), :mangaid
)