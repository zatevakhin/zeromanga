# -*- coding: utf-8 -*-

from core.download import MangaControl
import tornado.web as web
import logging
import zipfile
import os

from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


class ZipThumbnails(web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(ZipThumbnails, self).__init__(application, request)
        data = kwargs.get("data", {})
        self.manga = data.get("manga", None)
        self.mangastorage = data.get("manga-storage")

    def readf(self, fname, buffsz=4096):
        file_sz = os.path.getsize(fname)
        self.set_header('Content-Type', "application/zip")
        self.set_header('Content-Length', file_sz)

        with open(fname, 'rb') as f:
            while True:
                data = f.read(buffsz)

                if not data:
                    break

                self.write(data)

        self.finish()

    @staticmethod
    def makezip(fzip, dzip):
        with zipfile.ZipFile(fzip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for fname in os.listdir(dzip):
                zf.write(os.path.join(dzip, fname), fname[:-4])


    def get(self, mangaid, chaptid):

        chapter = self.manga.get_manga_chapt(mangaid, chaptid)

        if not chapter:
            self.send_error(404)
            return

        chaptname = "{}. {}".format(chapter["index"], chapter["chapter"])

        manga_chapter = MangaControl.chapterpath(self.mangastorage, chapter["path"], chaptname)

        manga_thumbnails = MangaControl.thumbpath(self.mangastorage, chapter["path"], chapter["chash"])

        tdzip = os.path.join(MangaControl.metapath(self.mangastorage, chapter["path"]), "z")

        czip = os.path.join(tdzip, "{}.zip".format(chaptid))

        # Если папки с архивами миниатюр нету то сделаем
        if not os.path.exists(tdzip):
            os.makedirs(tdzip)

        # Если папки с миниатюрами нету то сделаем
        if not os.path.exists(manga_thumbnails):
            os.makedirs(manga_thumbnails)

        if len(os.listdir(manga_thumbnails)) != chapter["pages"]:

            for t in range(1, chapter["pages"] + 1):

                if not os.path.exists(os.path.join(manga_thumbnails, "{}.jpg".format(t))):

                    logging.debug("Create thumbnail: %s", os.path.join(manga_thumbnails, "{}.jpg".format(t)))

                    img = Image.open(os.path.join(manga_chapter, "{}.png".format(t)))

                    img.thumbnail((200, 264), Image.ANTIALIAS)

                    img.convert("RGB").save(os.path.join(manga_thumbnails, "{}.jpg".format(t)), "JPEG", quality=95, optimize=True)

        if not os.path.exists(czip):
            self.makezip(czip, manga_thumbnails)

        if not os.path.exists(czip):
            self.send_error(404)
            return

        self.readf(czip)

