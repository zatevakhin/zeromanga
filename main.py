#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tornado import ioloop
from tornado import web
import argparse

from core import Install
from core import Manga
from core import Users
from core import Base

from core import TaskManager

from handlers import *

import logging
import sys
import os

logging.basicConfig(
    format='[%(asctime)s][%(levelname)-8s] (%(filename)s:%(lineno)d): %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO
    # filename="zeromanga.log"
)


class ZeroMangaApplication(object):
    def __init__(self):
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

    def main(self, addres, port):
        application = web.Application(self.__handlers, **self.__settings)
        application.listen(int(port), address=addres)
        ioloop.IOLoop.instance().start()

    @staticmethod
    def args():
        p = argparse.ArgumentParser()
        p.add_argument('--listen', '-l', nargs='?', default='8888')
        p.add_argument('--bind', '-b', nargs='?', default='0.0.0.0')
        p.add_argument('--manga', '-m', nargs='?', default='$HOME/.manga/')
        p.add_argument('--install', action='store_true', help="Creating database with initial groups and users.")
        return p.parse_args()

app_argv = ZeroMangaApplication.args()


BIND_ADDRES = app_argv.bind
PORT_NUMBER = app_argv.listen


data = {"download-threads": 8, "storage": os.path.expandvars(app_argv.manga)}

db = Base(os.path.join(os.path.expandvars(app_argv.manga), 'zeromanga.sqlite'))
data["db"] = db

users = Users(data)
data["users"] = users

if app_argv.install:
    ins = Install(data)
    ins.run_install()
    sys.exit()

data["manga"] = Manga(data)
data["taskman"] = TaskManager(data)

zmApp = ZeroMangaApplication()

zmApp.add_setting({"cookie_secret": "314a18af209b9dc253d3577a79c8840e5bde80e5"})
zmApp.add_setting({"template_path": "www/templates/"})
zmApp.add_setting({"static_path": "www/static"})
zmApp.add_setting({"login_url": "/login"})
zmApp.add_setting({"debug": True})

zmApp.add_handle((r'^/s/(.*)$', web.StaticFileHandler, {"path": "www/static/"}))

zmApp.add_handle((r'^/t/([a-f0-9]{40})/([a-f0-9]{32})/([0-9]+)$', Thumbnails, {"data": data}))

zmApp.add_handle((r'^/p/([a-f0-9]{40})/([a-f0-9]{32})/([0-9]+)$', Page, {"data": data}))
zmApp.add_handle((r'^/r/([a-f0-9]{40})/([a-f0-9]{32})$', RandomPage, {"data": data}))
zmApp.add_handle((r'^/m/([a-f0-9]{40})/c/([0-9]+)$', Covers, {"data": data}))
zmApp.add_handle((r'^/manga/([a-f0-9]{40})$', View, {"data": data}))

zmApp.add_handle((r'^/wsapi$', WebsocketAPI, {"data": data}))
zmApp.add_handle((r'^/api$', API, {"data": data}))

# Admin area handlers
zmApp.add_handle((r'^/adm$',       AdminArea, {"data": data}))
zmApp.add_handle((r'^/users$',     UsersControl, {"data": data}))
zmApp.add_handle((r'^/processes$', Processes, {"data": data}))
zmApp.add_handle((r'^/mupload$',   MangaUpload, {"data": data}))


zmApp.add_handle((r'^/profile$', Profile,     {"data": data}))
zmApp.add_handle((r'^/search$',  Search,      {"data": data}))
zmApp.add_handle((r'^/logout$',  Logout,      {"data": data}))
zmApp.add_handle((r'^/login$',   Login,       {"data": data}))
zmApp.add_handle((r'^/$',        Index,       {"data": data}))


if __name__ == "__main__":

    try:
        logging.info("Starting Zero/Manga server on %s:%s", BIND_ADDRES, PORT_NUMBER)

        logging.info("0/Manga - config: {}".format({
            "listen": app_argv.listen,
            "bind": app_argv.bind,
            "manga": os.path.expandvars(app_argv.manga)
        }))

        zmApp.main(BIND_ADDRES, PORT_NUMBER)
    except KeyboardInterrupt:
        logging.info("Stopping server!")
