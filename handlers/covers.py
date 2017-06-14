# -*- coding: utf-8 -*-

from core import BaseRequestHandler
from core import MangaItem
import os


class Covers(BaseRequestHandler):

    def initialize(self, data):
        self.db = data.get("db",  None)
        self.storage = data.get("storage")

    def get(self, mangaid, coverid):
        mitem = MangaItem(self.db, mangaid)

        if not mitem.manga:
            self.send_error(404)
            return

        coverp = os.path.join(self.storage, mitem.path, ".meta", "c", "{}.png".format(coverid))
        if not os.path.exists(coverp):
            self.send_error(404)
            return

        self.writef(coverp, "image/png")