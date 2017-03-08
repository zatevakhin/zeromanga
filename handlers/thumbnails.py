# -*- coding: utf-8 -*-

from core.download import MangaControl
import tornado.web as web
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
        self.mangastorage = data.get("manga-storage")

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

    def get(self, mangaid, chaptid, thumbid):

        chapter = self.manga.get_manga_chapt(mangaid, chaptid)

        # Если главы нету то 404
        if not chapter:
            self.send_error(404)
            return

        chaptname = "{}. {}".format(chapter["index"], chapter["chapter"])

        manga_chapter = MangaControl.chapterpath(self.mangastorage, chapter["path"], chaptname)

        manga_thumbnails = MangaControl.thumbpath(self.mangastorage, chapter["path"], chapter["chash"])

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
