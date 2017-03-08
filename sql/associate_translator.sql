INSERT OR IGNORE INTO manga_translators (translator_id, manga_id) VALUES (
  (SELECT id FROM translators WHERE value == :translator), :mangaid
)