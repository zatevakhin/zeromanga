# -*- coding: utf-8 -*-

from core import BaseRequestHandler
from core import MangaItem

from random import randint as rand
import os


class RandomPage(BaseRequestHandler):

    def initialize(self, data):
        self.db = data.get("db",  None)
        self.storage = data.get("storage")

    def get(self, mhash, chash):

        mitem = MangaItem(self.db, mhash)
        chapter = mitem.get_chapter(chash)

        if not chapter:
            self.send_error(404)
            return

        pagep = os.path.join(self.storage, mitem.path, chash, "{}.png".format(rand(1, chapter["pages"])))

        if not os.path.exists(pagep):
            self.send_error(404)
            return

        self.writef(pagep, "image/png")

