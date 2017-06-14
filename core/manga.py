# -*- coding: utf-8 -*-

from core import Base
from core.users import aux
import os


class Manga(object):

    def __init__(self, data):
        self.db = data.get("db")

    @property
    def count(self):

        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute('''SELECT COUNT(`id`) AS count FROM `manga`;''').fetchone().get("count", 0)

    def add_url(self, uiid, url):

        with self.db.connect() as connection:
            c = connection.cursor()
            c.execute(Base.source("sql/add_url.sql"), (uiid, url, aux.sha1(url)))

    def get_queued_by_hash(self, uhash):

        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute(Base.source("sql/url_exists.sql"), {"hash": uhash}).fetchone()

    def remove_queued_by_hash(self, uhash):
        with self.db.connect() as connection:
            c = connection.cursor()
            c.execute("DELETE FROM upload_queue WHERE uhash = :hash", {"hash": uhash})
            connection.commit()

    def get_queued(self):

        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute(Base.source("sql/qupload.sql")).fetchall() or []

    def get_index_manga(self, articles, offset):
        with self.db.connect() as connection:
            c = connection.cursor()
            selected = c.execute(
                '''SELECT mhash, name, english, original, covers, translation, state FROM manga LIMIT ? OFFSET ?;''',
                (articles, offset)
            ).fetchall()

            for manga in selected:
                manga.update({"title": (manga["name"] or manga["english"] or manga["original"])})

                manga["translation"] = manga["translation"] in ["завершен"]
                manga["state"] = manga["state"] in ["завершена"]

            return selected

    def get_manga_by_hash(self, mhash):
        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute(Base.source("sql/get_manga_by_hash.sql"), {"hash": mhash}).fetchone()

    def get_manga_chapt(self, mhash, chash):
        with self.db.connect() as connection:
            return connection.cursor().execute(Base.source("sql/get_chapter.sql"), {
                "mhash": mhash,
                "chash": chash
            }).fetchone()


class MangaItem(object):

    _MANGA = None
    _CHAPTERS = None
    _TRANSLATORS = None
    _GENRES = None
    _AUTHORS = None

    def __init__(self, db, mhash):
        self.hash = mhash
        self.db = db  # type: Base
        self.connection = self.db.connect()
        self._MANGA = self.manga


    @property
    def manga(self) -> dict:
        if not self._MANGA:
            with self.connection as c:
                return c.execute(Base.source("sql/get_manga_by_hash.sql"), {"hash": self.hash}).fetchone()
        return self._MANGA

    @property
    def miid(self) -> str:
        return self.manga["id"]

    @property
    def mhash(self) -> str:
        return self.manga["mhash"]

    @property
    def url(self) -> str:
        return self.manga["url"]

    @property
    def resource(self) -> str:
        return self.manga["resource"]

    @property
    def title(self) -> str:
        return self.manga["name"] or self.manga["english"] or self.manga["original"]

    @property
    def path(self) -> str:
        return os.path.join(self.resource, self.manga["mhash"])

    @property
    def description(self) -> str:
        return self.manga["description"]

    @property
    def volumes(self) -> str:
        return self.manga["volumes"]

    @property
    def state(self) -> str:
        return self.manga["state"]

    @property
    def translation(self) -> str:
        return self.manga["translation"]

    @property
    def covers(self) -> str:
        return self.manga["covers"]

    @property
    def year(self) -> str:
        return self.manga["year"]

    @property
    def translators(self) -> list:
        if not self._TRANSLATORS:
            with self.connection as c:
                t = c.execute(Base.source("sql/select_translators_by_miid.sql"), {"miid": self.miid}).fetchall()
                self._TRANSLATORS = list(map(lambda x: x["value"], t))

        return self._TRANSLATORS

    @property
    def genres(self) -> list:
        if not self._GENRES:
            with self.connection as c:
                t = c.execute(Base.source("sql/select_genres_by_miid.sql"), {"miid": self.miid}).fetchall()
                self._GENRES = list(map(lambda x: x["value"], t))

        return self._GENRES

    @property
    def authors(self) -> list:
        if not self._AUTHORS:
            with self.connection as c:
                t = c.execute(Base.source("sql/select_authors_by_miid.sql"), {"miid": self.miid}).fetchall()
                self._AUTHORS = list(map(lambda x: x["value"], t))

        return self._AUTHORS


    @property
    def chapters(self) -> list:
        if not self._CHAPTERS:
            with self.connection as c:
                self._CHAPTERS = c.execute(
                    '''SELECT *, 0 AS readed FROM chapters WHERE mangaid = ? ORDER BY `index`''', [self.miid]
                ).fetchall()

        return self._CHAPTERS

    def get_chapter(self, chash):
        with self.connection as c:
            return c.execute(Base.source("sql/get_chapter.sql"), {
                "mhash": self.mhash,
                "chash": chash
            }).fetchone()

    def get_readed_count(self, ciid, uiid):
        if not uiid:
            return 0

        with self.connection as c:
            return c.execute(Base.source("sql/select_readed_count.sql"), {
                "miid": self.miid,
                "ciid": ciid,
                "uiid": uiid
            }).fetchone().get("readed", 0)

    def get_readed(self, ciid, uiid):
        if not uiid:
            return []

        with self.connection as c:
            readed = c.execute(Base.source("sql/select_readed.sql"), {
                "miid": self.miid,
                "ciid": ciid,
                "uiid": uiid
            }).fetchall()

            return list(map(lambda x: x["pageid"], readed))

    def set_readed(self, uiid, ciid, piid):
        with self.connection as c:
            c.execute(Base.source("sql/set_page_readed.sql"), {
                "miid": self.miid,
                "pgid": piid,
                "uiid": uiid,
                "ciid": ciid
            })
