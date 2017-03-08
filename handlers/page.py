# -*- coding: utf-8 -*-

import tornado.web as web
from core import Base
import os


class Page(web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(Page, self).__init__(application, request)
        data = kwargs.get("data", {})
        self.db = data.get("db",  None)
        self.manga = data.get("manga",  None)
        self.users = data.get("users",  None)
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

    def get(self, mhash, chash, imageid):

        chapter = self.manga.get_manga_chapt(mhash, chash)
        imageid = int(imageid)

        if not chapter:
            self.send_error(404)
            return

        if not 0 < imageid <= chapter["pages"]:
            self.send_error(404)
            return

        page = "{}.png".format(imageid)

        chapterp = "{}. {}".format(chapter["index"], chapter["chapter"])

        pagep = os.path.join(self.mangastorage, chapter["path"], chapterp, page)

        if not os.path.exists(pagep):
            self.send_error(404)
            return

        self.readf(pagep)

        cookie = self.get_secure_cookie("dfsid", None)

        if not cookie:
            return

        cookie = cookie.decode()

        user = self.users.get_by_cookie(cookie)

        if not user:
            return

        with self.db.connect() as connection:
            c = connection.cursor()

            c.execute(Base.source("sql/set_page_readed.sql"), {
                "pgid": imageid,
                "uiid": user["id"],
                "ciid": chapter["id"],
                "miid": chapter["mangaid"]
            })
