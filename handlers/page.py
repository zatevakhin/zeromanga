# -*- coding: utf-8 -*-

from core import BaseRequestHandler
from core import MangaItem
from core import Base
import os


class Page(BaseRequestHandler):

    def initialize(self, data):
        super(Page, self).initialize(**data)
        self.storage = data.get("storage")  # type: str
        self.db = data.get("db",  None)  # type: Base

    def get(self, mhash, chash, imageid):

        mitem = MangaItem(self.db, mhash)
        chapter = mitem.get_chapter(chash)
        imageid = int(imageid)

        if not chapter:
            self.send_error(404)
            return

        if not 0 < imageid <= chapter["pages"]:
            self.send_error(404)
            return

        page = "{}.png".format(imageid)

        pagep = os.path.join(self.storage, mitem.path, chash, page)

        if not os.path.exists(pagep):
            self.send_error(404)
            return

        self.writef(pagep, "image/png")

        user = self.get_userdata()

        if not user:
            return

        mitem.set_readed(user["id"], chapter["id"], imageid)
