

CREATE TABLE IF NOT EXISTS `users` (
      `id`     INTEGER      PRIMARY KEY NOT NULL,
      `uhid`   CHAR(40)     UNIQUE      NOT NULL,
      `login`  VARCHAR(16)  UNIQUE      NOT NULL,
      `passwd` VARCHAR(128)             NOT NULL,
      `group_id` INTEGER                NOT NULL,

      FOREIGN KEY (group_id) REFERENCES groups(id)
);

CREATE TABLE IF NOT EXISTS groups (
  id   INTEGER PRIMARY KEY NOT NULL,
  name VARCHAR(16) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS `authorized` (
      `id`     INTEGER     PRIMARY KEY      NOT NULL,
      `uiid`   INTEGER                      NOT NULL,
      `ip`     VARCHAR(16)                  NOT NULL,
      `cookie` CHAR(40)                     NOT NULL,
      `stamp`  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (uiid) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS `upload_queue` (
  `id`   INTEGER PRIMARY KEY         NOT NULL,
  -- User Integer ID
  `uiid`  INTEGER                    NOT NULL,
  `url`   TEXT                       NOT NULL,
  -- URL hash id
  `uhash` CHAR(40) UNIQUE            NOT NULL,
  `stamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (uiid) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS `genres` (
  `id`    INTEGER      PRIMARY KEY NOT NULL,
  `value` VARCHAR(256) UNIQUE      NOT NULL
);

CREATE TABLE IF NOT EXISTS `translators` (
  `id`    INTEGER      PRIMARY KEY NOT NULL,
  `value` VARCHAR(256) UNIQUE      NOT NULL
);

CREATE TABLE IF NOT EXISTS `authors` (
  `id`    INTEGER      PRIMARY KEY NOT NULL,
  `value` VARCHAR(256) UNIQUE      NOT NULL
);

CREATE TABLE IF NOT EXISTS `chapters` (
  `id`      INTEGER     PRIMARY KEY NOT NULL,
  `mangaid` INTEGER                 NOT NULL,
  `chash`   CHAR(32)                NOT NULL,
  `chapter` TEXT                    NOT NULL,
  `pages`   INTEGER                 NOT NULL,
  `index`   INTEGER                 NOT NULL,

  UNIQUE (mangaid, chash),

  FOREIGN KEY (mangaid) REFERENCES manga(id)
);

CREATE TABLE IF NOT EXISTS manga (
  id          INTEGER PRIMARY KEY NOT NULL,
  mhash       CHAR(40) UNIQUE     NOT NULL,
  url         TEXT                NOT NULL,
  resource    TEXT                NOT NULL,
  name        TEXT                        ,
  english     TEXT                        ,
  original    TEXT                        ,
  description TEXT                        ,
  covers      INTEGER             NOT NULL,
  volumes     INTEGER             NOT NULL,
  chapters    INTEGER             NOT NULL,
  mature      TINYINT             NOT NULL,
  single      TINYINT             NOT NULL,
  year        VARCHAR(32)         NOT NULL,
  translation VARCHAR(64)         NOT NULL,
  state       VARCHAR(64),
  rating      VARCHAR(32)
);

CREATE TABLE IF NOT EXISTS `manga_genres` (
  `genre_id` INTEGER NOT NULL,
  `manga_id` INTEGER NOT NULL,

  FOREIGN KEY (genre_id) REFERENCES genres(id),
  FOREIGN KEY (manga_id) REFERENCES manga(id),

  UNIQUE (genre_id, manga_id)
);

CREATE TABLE IF NOT EXISTS `manga_authors` (
  `author_id` INTEGER NOT NULL,
  `manga_id`  INTEGER NOT NULL,

  FOREIGN KEY (author_id) REFERENCES authors(id),
  FOREIGN KEY (manga_id) REFERENCES manga(id),

    UNIQUE (author_id, manga_id)
);

CREATE TABLE IF NOT EXISTS `manga_translators` (
  `translator_id` INTEGER NOT NULL,
  `manga_id`      INTEGER NOT NULL,

  FOREIGN KEY (translator_id) REFERENCES translators(id),
  FOREIGN KEY (manga_id) REFERENCES manga(id),

  UNIQUE (translator_id, manga_id)
);

CREATE TABLE IF NOT EXISTS `uread` (
  `userid`  INTEGER NOT NULL,
  `mangaid` INTEGER NOT NULL,
  `chaptid` INTEGER NOT NULL,
  `pageid`  INTEGER NOT NULL,

  UNIQUE (userid, mangaid, chaptid, pageid),

  FOREIGN KEY (userid) REFERENCES users(id),
  FOREIGN KEY (mangaid) REFERENCES manga(id),
  FOREIGN KEY (chaptid) REFERENCES chapters(id)
);