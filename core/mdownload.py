# -*- coding: utf-8 -*-

from core.database import Base
from core.util import json
from core.util import aux

from urllib.parse import urlparse
from PIL import Image
import progressbar
import requests
import logging
import io
import os


class MangaDownload(object):

    _PLUGIN = None

    def __init__(self, tm, work):
        self.work = work
        self.data = work.get("data")
        self.tm = tm

    @property
    def uhash(self):
        return self.data["uhash"]

    @property
    def storage(self):
        return self.work["storage"]

    @property
    def resource(self):
        if "resource" not in self.data:
            self.data["resource"] = urlparse(self.data["url"]).netloc
        return self.data["resource"]

    @property
    def plugin(self):
        if not self._PLUGIN:
            self._PLUGIN = self.tm.get_plugin(self.resource)
        return self._PLUGIN

    @property
    def p_manga(self):
        return os.path.join(self.storage, self.resource, self.uhash)

    @property
    def p_meta(self):
        return os.path.join(self.p_manga, ".meta")

    @property
    def p_info(self):
        return os.path.join(self.p_meta, "info.json")

    @property
    def p_covers(self):
        return os.path.join(self.p_meta, "c")

    def p_chapt(self, c):
        return os.path.join(self.p_manga, c)

    def get_info(self):
        return self.plugin.run("info", self.data.get("url"))

    def save_info(self):
        info = self.get_info()

        info = {**self.data, **info, "path": self.p_manga, "ch_count": 0}

        if not info:
            raise ValueError({"msg": "Can`t get info!", "code": 1})

        self.make_path(self.p_meta)
        self.make_path(self.p_covers)

        self.save_image_list(self.p_covers, info.get("covers", []))

        self.save_info_in_db(info)

        return info

    def save_info_in_db(self, info):
        logging.info("Saving manga in db with id=%s", info.get("uhash"))
        db = self.work.get("db")

        with db.connect() as connection:
            c = connection.cursor()
            c.execute(Base.source("sql/insert_manga.sql"), info)

            mangaid = c.lastrowid

            c.executemany(Base.source("sql/insert_genre.sql"), map(lambda x: tuple([x]), info["genres"]))
            c.executemany(Base.source("sql/insert_author.sql"), map(lambda x: tuple([x]), info["authors"]))
            c.executemany(Base.source("sql/insert_translator.sql"), map(lambda x: tuple([x]), info["translators"]))

            for genre in info["genres"]:
                c.execute(Base.source("sql/associate_genre.sql"), {
                    "mangaid": mangaid,
                    "genre": genre
                })

            for author in info["authors"]:
                c.execute(Base.source("sql/associate_author.sql"), {
                    "mangaid": mangaid,
                    "author": author
                })

            for translator in info["translators"]:
                c.execute(Base.source("sql/associate_translator.sql"), {
                    "mangaid": mangaid,
                    "translator": translator
                })

            connection.commit()

    def save_chapters(self, info):
        info["chapters"] = self.plugin.run("chapters", self.data.get("url"))
        info["ch_count"] = len(info["chapters"])

        db = self.work.get("db")

        with db.connect() as connection:
            c = connection.cursor()
            c.execute('''UPDATE manga SET chapters=:ch_count WHERE mhash=:uhash''', info)
            connection.commit()

        for chapter in info["chapters"]:
            chapter["chash"] = aux.md5(chapter["url"])
            if self.check_is_chapter_exists(info.get("uhash"), chapter):
                logging.info("Skipping '%s' chapter, already exists!", chapter["title"])
                continue

            self.chapter(info, chapter)
            self.save_chapter_in_db(info, chapter)
        return info

    def check_is_chapter_exists(self, mhash, chapter):
        db = self.work.get("db")
        with db.connect() as connection:
            c = connection.cursor()
            return c.execute('''SELECT c.*, m.* FROM
                          chapters AS c JOIN
                          manga AS m ON c.mangaid = m.id
                        WHERE m.mhash = ? AND c.chash = ? AND c.`index` = ?''', [
                mhash, chapter["chash"], chapter["index"]
            ]).fetchone()

    def save_chapter_in_db(self, info, chapter):
        db = self.work.get("db")

        with db.connect() as connection:
            c = connection.cursor()

            c.execute(Base.source("sql/insert_chapter.sql"), {
                "chapter": chapter["title"],
                "chash": chapter["chash"],
                "pages": chapter["count"],
                "index": chapter["index"],
                "uhash": info.get("uhash")
            })

            connection.commit()

    def save_image_list(self, path, images):
        bar = progressbar.ProgressBar(redirect_stdout=True, max_value=len(images))

        for index, url in enumerate(images):
            image = os.path.join(path, "{}.{}".format(index + 1, "png"))

            if not os.path.exists(image):
                self.get(url, image)

            bar.update(index + 1)
        bar.finish()

    @staticmethod
    def make_path(path):
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def get(url, path):
        extension = str(url.split(".")[-1]).lower()

        r = requests.get(url, stream=True, timeout=60)

        if extension in ["png"]:
            with open(path, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return

        image = Image.open(io.BytesIO(r.content))

        if image.mode in ["CMYK"]:
            image = image.convert("RGBA")

        image.save(path)

    def chapter(self, info, chapter):
        p_chapt = self.p_chapt(chapter["chash"])
        self.make_path(p_chapt)

        logging.info("Downloading '%s'.", chapter["title"])

        pages = self.plugin.run("pages", chapter["url"], info["mature"])

        chapter.update({"pages": pages, "count": len(pages)})

        self.save_image_list(p_chapt, chapter["pages"])

    def save(self):
        info = self.save_info()

        info = self.save_chapters(info)

        logging.info("Saving info into file: %s", self.p_info)

        with open(self.p_info, 'w') as f:
            f.write(json.dumps(info, indent=2))
