INSERT OR IGNORE INTO manga_authors (author_id, manga_id) VALUES (
  (SELECT id FROM authors WHERE value == :author), :mangaid
)