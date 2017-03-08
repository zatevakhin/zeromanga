# -*- coding: utf-8 -*-

from core import Base
from core.users import aux


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

    def url_exists(self, url):

        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute(Base.source("sql/url_exists.sql"), {"hash": aux.sha1(url)}).fetchone()

    def get_queued_by_hash(self, uhash):

        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute(Base.source("sql/url_exists.sql"), {"hash": uhash}).fetchone()

    def get_queued(self):

        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute(Base.source("sql/qupload.sql")).fetchall() or []

    def get_index_manga(self, articles, offset):
        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute('''SELECT mhash, title, covers FROM manga LIMIT ? OFFSET ?;''', (
                articles, offset)).fetchall()

    def get_manga_by_hash(self, mhash):
        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute('''SELECT * FROM manga WHERE mhash == :hash LIMIT 1;''', {
                "hash": mhash
            }).fetchone()

    def get_manga_chapt(self, mhash, chash):
        with self.db.connect() as connection:
            return connection.cursor().execute(Base.source("sql/get_chapter.sql"), {
                "mhash": mhash,
                "chash": chash
            }).fetchone()

    def get_manga_full(self, mhash):

        with self.db.connect() as connection:
            c = connection.cursor()
            data = c.execute('''SELECT * FROM manga WHERE mhash == :hash LIMIT 1;''', {
                "hash": mhash
            }).fetchone() or {}

            querydata = {"miid": data["id"]}

            data["chapters"] = c.execute(
                '''SELECT *, 0 AS readed FROM chapters WHERE mangaid = :miid''',
                querydata
            ).fetchall() or {}

            data["genres"] = c.execute(
                Base.source("sql/select_genres_by_miid.sql"),
                querydata
            ).fetchall() or {}

            data["authors"] = c.execute(
                Base.source("sql/select_authors_by_miid.sql"),
                querydata
            ).fetchall() or {}

            data["translators"] = c.execute(
                Base.source("sql/select_translators_by_miid.sql"),
                querydata
            ).fetchall() or {}

            translators = []
            for item in data["translators"]:
                if "value" in item:
                    translators.append(item["value"])

            data["translators"] = translators

            authors = []
            for item in data["authors"]:
                if "value" in item:
                    authors.append(item["value"])

            data["authors"] = authors

            genres = []
            for item in data["genres"]:
                if "value" in item:
                    genres.append(item["value"])

            data["genres"] = genres

            return data
