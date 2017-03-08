# -*- coding: utf-8 -*-

import tornado.web as web
import os


class Covers(web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(Covers, self).__init__(application, request)
        data = kwargs.get("data", {})
        self.db = data.get("db",  None)
        self.manga = data.get("manga",  None)
        self.mangastorage = data.get("manga-storage")

    def get(self, mangaid, coverid):

        manga = self.manga.get_manga_by_hash(mangaid)

        if not manga:
            self.send_error(404)
            return

        coverp = os.path.join(self.mangastorage, manga["path"], ".meta", "c", "{}.png".format(coverid))

        if not os.path.exists(coverp):
            self.send_error(404)
            return

        file_sz = os.path.getsize(coverp)
        self.set_header('Content-Type', 'image/png')
        self.set_header('Content-Length', file_sz)

        with open(coverp, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                self.write(data)
        self.finish()
