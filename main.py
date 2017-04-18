#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tornado import ioloop
from tornado import web

from core import MangaControl
from core import Manga
from core import Users
from core import Base

from handlers import *

import logging

logging.basicConfig(
    format='[%(asctime)s][%(levelname)-8s] (%(filename)s:%(lineno)d): %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG
    # filename="zeromanga.log"
)


class ZeroMangaApplication(object):
    def __init__(self, addres, port):
        self.__port = int(port)
        self.__addr = addres
        self.__handlers = []
        self.__settings = {}

    def add_handle(self, handle):
        if type(handle) == tuple:
            self.__handlers.append(handle)
        else:
            raise AssertionError("Handler must be tuple!")

    def add_setting(self, settings):
        if type(settings) == dict:
            self.__settings.update(settings)
        else:
            raise AssertionError("Setting must be dict!")

    def main(self):
        application = web.Application(self.__handlers, **self.__settings)
        application.listen(self.__port, address=self.__addr)
        ioloop.IOLoop.instance().start()

data = {
    "db": Base('zeromanga.sqlite'),
    "download-threads": 8,
    "manga-storage": "/mnt/storage1/manga"
}

data["mangadownload"] = MangaControl(data)
data["users"] = Users(data)
data["manga"] = Manga(data)


BIND_ADDRES = '0.0.0.0'
PORT_NUMBER = 8888

logging.info("Starting Zero/Manga server on %s:%s", BIND_ADDRES, PORT_NUMBER)
zmApp = ZeroMangaApplication(BIND_ADDRES, PORT_NUMBER)

zmApp.add_setting({"cookie_secret": "314a18af209b9dc253d3577a79c8840e5bde80e5"})
zmApp.add_setting({"template_path": "www/templates/"})
zmApp.add_setting({"static_path": "www/static"})
zmApp.add_setting({"login_url": "/login"})
zmApp.add_setting({"debug": True})

zmApp.add_handle((r'^/s/(.*)$', web.StaticFileHandler, {"path": "www/static/"}))

zmApp.add_handle((r'^/t/([a-f0-9]{40})/([a-f0-9]{32})/([0-9]+)$', Thumbnails, {"data": data}))
zmApp.add_handle((r'^/z/([a-f0-9]{40})/([a-f0-9]{32})$', ZipThumbnails, {"data": data}))

zmApp.add_handle((r'^/p/([a-f0-9]{40})/([a-f0-9]{32})/([0-9]+)$', Page, {"data": data}))
zmApp.add_handle((r'^/r/([a-f0-9]{40})/([a-f0-9]{32})$', RandomPage, {"data": data}))
zmApp.add_handle((r'^/m/([a-f0-9]{40})/c/([0-9]+)$', Covers, {"data": data}))
zmApp.add_handle((r'^/manga/([a-f0-9]{40})$', View, {"data": data}))

zmApp.add_handle((r'^/wsapi$', WebsocketAPI, {"data": data}))

# Admin area handlers
zmApp.add_handle((r'^/adm$',       AdminArea, {"data": data}))
zmApp.add_handle((r'^/processes$', Processes, {"data": data}))
zmApp.add_handle((r'^/uqueue$',   UploadQueue, {"data": data}))


zmApp.add_handle((r'^/profile$', Profile,     {"data": data}))
zmApp.add_handle((r'^/search$',   Search,      {"data": data}))
zmApp.add_handle((r'^/login$',   Login,       {"data": data}))
zmApp.add_handle((r'^/$',        Index,       {"data": data}))


if __name__ == "__main__":
    try:
        zmApp.main()
    except KeyboardInterrupt:
        logging.info("Stopping server!")
