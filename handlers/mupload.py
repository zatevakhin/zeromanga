# -*- coding: utf-8 -*-

from core.taskmanager import TaskManager

from core.util import aux

from core import BaseRequestHandler
from core import Manga
from core import Base

from tornado import web
from urllib.parse import urlparse
from random import shuffle
import re


DEFAULT_URLS = [
    "http://mintmanga.com/some_manga",
    "http://readmanga.me/some_manga"
]


class MangaUpload(BaseRequestHandler):
    RESOURCES = []

    def initialize(self, data):
        super(MangaUpload, self).initialize(**data)
        self.taskman = data.get("taskman", None) # type: TaskManager
        self.manga = data.get("manga", None) # type: Manga
        self.db = data.get("db", None) # type: Base

        self.RESOURCES = self.taskman.get_resources()

    @web.authenticated
    def get(self):
        if not self.groups_allowed_access(["admins"]):
            return

        self.render(
            "mupload.tt",
            title="0/Manga: Очередь загружаемой манги!",
            mqueued=self.manga.get_queued(),
            resources=",".join(self.RESOURCES)
        )

    @web.authenticated
    def post(self):
        if not self.groups_allowed_access(["admins"]):
            return

        action = self.get_argument("action", None)

        if action in ["manga-add"]:
            url = self.get_argument("url", None)

            if not url:
                self.write({"status": "error", "msg": "Not enought arguments"})
                return

            self.manga_add(url)

        elif action in ["manga-remove"]:
            uhash = self.get_argument("uhash", None)

            if not uhash:
                self.write({"status": "error", "msg": "Not enought arguments"})
                return

            self.manga_remove(uhash)

        elif action in ["manga-upload"]:
            uhash = self.get_argument("uhash", None)

            if not uhash:
                self.write({"status": "error", "msg": "Not enought arguments"})
                return

            self.manga_upload(uhash)


    def get_random_manga_url(self):
        with self.db.connect() as connection:
            urls = list(map(lambda x: x["url"], connection.execute("SELECT url FROM manga LIMIT 100").fetchall()))

            if not urls:
                urls = DEFAULT_URLS

            shuffle(urls)

            return urls[0]

    def manga_add(self, url):
        regex = "|".join(map(lambda x: "http://" + x, self.RESOURCES)).replace(".", "\\.")
        rex = re.compile("^({0})/[a-z0-9_]+$".format(regex), re.I)

        if not rex.match(url):
            self.write({"status": "error", "msg": "resource is not supported!"})
            return

        uhash = aux.sha1(url)
        if self.manga.get_queued_by_hash(uhash):
            self.write({"status": "error", "msg": "This URL already added in queue for download!"})
            return

        if self.manga.get_manga_by_hash(uhash):
            self.write({"status": "error", "msg": "This manga already downloaded!"})
            return

        user = self.get_userdata()
        self.manga.add_url(user["id"], url)
        self.write({"status": "ok", "msg": "Manga added in queue"})

    def manga_remove(self, uhash):
        if not self.manga.get_queued_by_hash(uhash):
            self.write({"status": "error", "msg": "We not have manga with this id={} in upload queue!".format(uhash)})
            return

        self.manga.remove_queued_by_hash(uhash)
        self.write({"status": "ok", "msg": "Manga removed from queue"})

    def manga_upload(self, uhash):
        manga = self.manga.get_queued_by_hash(uhash)

        if not manga:
            self.write({"status": "error", "msg": "We not have manga with this id={} in upload queue!".format(uhash)})
            return

        resource = urlparse(manga["url"]).netloc
        self.taskman.add("download", uhash=uhash, resource=resource, url=manga["url"])

        self.write({"status": "ok", "msg": "Manga added in taskmanager to upload!"})
