# -*- coding: utf-8 -*-

from random import randint as rand
import tornado.web as web
import os


class RandomPage(web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(RandomPage, self).__init__(application, request)
        data = kwargs.get("data", {})
        self.db = data.get("db",  None)
        self.manga = data.get("manga",  None)
        self.mangastorage = data.get("manga-storage")

    # ============================================================================
    def readf(self, fname, buffsz=4096):
        file_sz = os.path.getsize(fname)
        self.set_header('Content-Type', "image/png")
        self.set_header('Content-Length', file_sz)

        with open(fname, 'rb') as f:
            while True:
                data = f.read(buffsz)

                if not data:
                    break

                self.write(data)

        self.finish()

    def get(self, mhash, chash):

        chapter = self.manga.get_manga_chapt(mhash, chash)

        if not chapter:
            self.send_error(404)
            return

        page = "{}.png".format(rand(1, chapter["pages"]))

        chapterp = "{}. {}".format(chapter["index"], chapter["chapter"])

        pagep = os.path.join(self.mangastorage, chapter["path"], chapterp, page)

        if not os.path.exists(pagep):
            self.send_error(404)
            return

        self.readf(pagep)

