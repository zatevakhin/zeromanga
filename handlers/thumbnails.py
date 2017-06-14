# -*- coding: utf-8 -*-

from tornado import web
import logging
import os

from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


class Thumbnails(web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(Thumbnails, self).__init__(application, request)
        data = kwargs.get("data", {})
        self.manga = data.get("manga", None)
        self.storage = data.get("storage")

    # ============================================================================
    def readf(self, fname, buffsz=4096):
        file_sz = os.path.getsize(fname)
        self.set_header('Content-Type', "image/jpeg")
        self.set_header('Content-Length', file_sz)

        with open(fname, 'rb') as f:
            while True:
                data = f.read(buffsz)

                if not data:
                    break

                self.write(data)

        self.finish()

    def get(self, mhash, chash, thumbid):

        chapter = self.manga.get_manga_chapt(mhash, chash)

        if not chapter:
            self.send_error(404)
            return

        manga_chapter = os.path.join(self.storage, chapter["resource"], mhash, chash)

        manga_thumbnails = os.path.join(self.storage, chapter["resource"], mhash, ".meta", "t", chash)

        current_thumb = os.path.join(manga_thumbnails, "{}.jpg".format(thumbid))

        # Если папки с миниатюрами нету то сделаем
        if not os.path.exists(manga_thumbnails):
            os.makedirs(manga_thumbnails)

        if not os.path.exists(current_thumb):
            logging.warning("Thumbnail '%s.png' not found!", thumbid)

            for t in range(1, chapter["pages"] + 1):

                if not os.path.exists(os.path.join(manga_thumbnails, "{}.jpg".format(t))):

                    logging.debug("Create thumbnail: %s", os.path.join(manga_thumbnails, "{}.jpg".format(t)))

                    img = Image.open(os.path.join(manga_chapter, "{}.png".format(t)))

                    img.thumbnail((200, 264), Image.ANTIALIAS)

                    img.convert("RGB").save(os.path.join(manga_thumbnails, "{}.jpg".format(t)), "JPEG", quality=95, optimize=True)

        if not os.path.exists(current_thumb):
            self.send_error(404)
            return

        self.readf(current_thumb)
