# -*- coding: utf-8 -*-

from multiprocessing.dummy import Pool
from urllib.parse import urlparse
from queue import Queue

from core.util import json
from core import plugin

import logging
import requests

from PIL import Image
import io
import os

from core.util.KTh import KThread

from core.database import Base
from core.util import aux


class MangaControl(object):

    PROCESSES = {}
    JOB_QUEUE = Queue()
    JOB_TRACK = None

    def __init__(self, data):
        self.MANGA_DIR = data.get("manga-storage")
        self.pool = Pool(data.get("download-threads"))
        self.mangastorage = data.get("manga-storage")
        self.db = data.get("db")

        self.plugins = plugin.load("core/plugins")

        self.JOB_TRACK = KThread(target=self.ttrack)
        self.JOB_TRACK.start()

    def add(self, url, uiid, uhash):
        self.PROCESSES[uhash] = {
            "task": "download",
            "status": "wait",
            "name": url,
            "current": 0,
            "all": 0
        }

        self.JOB_QUEUE.put({"url": url, "uiid": uiid, "uhash": uhash})

    def ttrack(self):
        while True:
            task = self.JOB_QUEUE.get()

            self.pool.apply_async(
                error_callback=self.fail,
                callback=self.complete,
                func=self.make,
                args=(task,),
            )

    @staticmethod
    def resource(job):
        return urlparse(job.get("url")).netloc

    @staticmethod
    def infopath(md, mp):
        return os.path.join(MangaControl.metapath(md, mp), 'info.json')

    @staticmethod
    def thumbpath(md, mp, chash):
        return os.path.join(MangaControl.metapath(md, mp), 't', chash)

    @staticmethod
    def metapath(md, mp):
        return os.path.join(MangaControl.mangapath(md, mp), '.meta')

    @staticmethod
    def chapterpath(md, mp, chash):
        return os.path.join(MangaControl.mangapath(md, mp), chash)

    @staticmethod
    def mangapath(md, mp):
        return os.path.join(md, mp)


    def make(self, job):
        logging.debug("<make:job url='%s'>", job.get("url"))

        # TODO: Распределение задач (загрузка, обновление, etc)
        try:

            return self.job_make(job)
        except Exception as e:
            logging.exception("In make: %s", e, exc_info=True)

    def job_make(self, job):
        job["resource"] = MangaControl.resource(job)

        cplugin = self.plugins[job["resource"]].replicate()

        print(cplugin)
        job["data"] = cplugin.run(job)
        job["data"]["uhash"] = job["uhash"]
        job["data"]["path"] = self.get_green_path(job["data"])

        self.PROCESSES[job["uhash"]].update({
            "task": "download",
            "status": "runing",
            "name": job["data"]["title"],
            "url": job["url"],
            "all": job["data"]["chapterscount"]
        })

        self.save_info(job["data"])
        self.save_manga(job, cplugin)

        return job

    def fail(self, *args, **kwargs):
        logging.error("<fail:job url='' args=(%s) kwargs=(%s)", args, kwargs)

    def complete(self, result):
        logging.debug("<complete:job url='%s'>", result["url"])
        self.PROCESSES[result["uhash"]].update({"status": "complete"})

        del self.PROCESSES[result["uhash"]]

        manga = result["data"]
        manga["url"] = result["url"]

        mangainfo = {
            "description": manga["description"],
            "translation": manga["translation"],
            "chapters": manga["chapterscount"],
            "covers": len(manga["covers"]),
            "volumes": manga["volumes"],
            "year": int(manga["year"]),
            "mature": manga["mature"],
            "single": manga["single"],
            "title": manga["title"],
            "hash": manga["uhash"],
            "path": manga["path"],
            "url": manga["url"],

            "state": manga.get("state", None),
            "rating": manga.get("rating", None),
        }

        with self.db.connect() as connection:
            c = connection.cursor()

            c.execute(Base.source("sql/insert_manga.sql"), mangainfo)

            mangaid = c.lastrowid

            c.executemany(Base.source("sql/insert_genre.sql"), map(lambda x: tuple([x]), manga["genres"]))
            c.executemany(Base.source("sql/insert_author.sql"), map(lambda x: tuple([x]), manga["authors"]))
            c.executemany(Base.source("sql/insert_translator.sql"), map(lambda x: tuple([x]), manga["translators"]))

            for genre in manga["genres"]:
                c.execute(Base.source("sql/associate_genre.sql"), {
                    "mangaid": mangaid,
                    "genre": genre
                })

            for author in manga["authors"]:
                c.execute(Base.source("sql/associate_author.sql"), {
                    "mangaid": mangaid,
                    "author": author
                })

            for translator in manga["translators"]:
                c.execute(Base.source("sql/associate_translator.sql"), {
                    "mangaid": mangaid,
                    "translator": translator
                })

            for chapter in manga["chapters"]:
                c.execute(Base.source("sql/insert_chapter.sql"), {
                    "chash": aux.md5(chapter["url"]),
                    "chapter": chapter["chapt"],
                    "pages": chapter["count"],
                    "index": chapter["index"],
                    "mangaid": mangaid
                })

    def get_green_path(self, data):

        titles = [data["name"]["ja"], data["name"]["en"], data["name"]["ru"]]
        titles = list(filter(bool, titles))

        default = titles[0]

        for path in filter((lambda z: os.path.exists(MangaControl.infopath(self.mangastorage, z))), titles):
            item = json.load(open(MangaControl.infopath(self.mangastorage, path)))
            if item.get("uhash", None) == data["uhash"]:
                default = path
                break

        return default

    def save_info(self, info):
        # --------------------------------------------------------------------------
        metad = os.path.join(self.MANGA_DIR, info["path"], ".meta/")
        if not os.path.exists(metad):
            os.makedirs(metad)

        # --------------------------------------------------------------------------
        coversd = os.path.join(metad, "c/")
        if not os.path.exists(coversd):
            os.makedirs(coversd)

        # --------------------------------------------------------------------------
        for index, url in enumerate(info["covers"]):
            self.download_and_convert(url, os.path.join(coversd, "{}.{}".format(index + 1, "png")))

        # --------------------------------------------------------------------------
        with open(os.path.join(metad, "info.json"), 'w') as f:
            f.write(json.dumps(info, indent=2))

    def save_manga(self, job, cplugin):

        if not job["data"]["chapters"]:
            return

        mangap = MangaControl.mangapath(self.mangastorage, job["data"]["path"])
        if not os.path.exists(mangap):
            os.makedirs(mangap)

        for chapter in job["data"]["chapters"]:
            self.PROCESSES[job["data"]["uhash"]].update({
                "current": chapter["index"]
            })

            # TODO: Убедится что в базу идет чистый хеш урла
            if job["data"]["mature"]:
                chapter.update({"url": "{}?mature=1".format(chapter["url"])})

            pages = cplugin.grab_pages(chapter)
            chapter.update({
                "count": len(pages),
                "pages": pages
            })

            chapterp = MangaControl.chapterpath(
                self.mangastorage,
                job["data"]["path"], "{}. {}".format(chapter["index"],chapter["chapt"])
            )

            MangaControl.download_chapter(chapterp, chapter, "png")
            # FIXME: УБРАТЬ
            # break

    @staticmethod
    def download_chapter(chapterp, chapter, images_format):
        images_format = images_format.lower()

        if not os.path.exists(chapterp):
            os.makedirs(chapterp)

        for index, url in enumerate(chapter["pages"]):
            imagep = os.path.join(chapterp, "{}.{}".format(index + 1, images_format))
            if not os.path.exists(imagep):
                MangaControl.download_and_convert(url, imagep)


    @staticmethod
    def download_and_convert(url, dest):
        extension = url.split(".")[-1].lower()

        if extension in ["png"]:
            MangaControl.simple_download(url, dest)
            return

        else:
            responce = requests.get(url, stream=True, timeout=60)
            image = Image.open(io.BytesIO(responce.content))

            if image.mode in ["CMYK"]:
                image = image.convert("RGBA")

            image.save(dest)

    @staticmethod
    def simple_download(url, p):
        r = requests.get(url, stream=True, timeout=60)
        with open(p, 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
