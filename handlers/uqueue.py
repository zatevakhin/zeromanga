# -*- coding: utf-8 -*-

from urllib.parse import urlparse
import tornado.web as web
import logging


class UploadQueue(web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(UploadQueue, self).__init__(application, request)

        data = kwargs.get("data", {})
        self.db = data.get("db",  None)
        self.users = data.get("users",  None)
        self.manga = data.get("manga",  None)
        self.mangadownload = data.get("mangadownload",  None)

    def get_current_user(self):
        cookie = self.get_secure_cookie("dfsid", None)

        if cookie and self.users.get_by_cookie(cookie.decode()):
            return cookie.decode()

        self.set_status(403)

    @web.authenticated
    def get(self):
        self.render(
            "uqueue.tt",
            title="Profile:!",
            mqueued=self.manga.get_queued()
        )

    @web.authenticated
    def post(self):
        print(self.request.body)

        action = self.get_argument("action", None)
        uhash = self.get_argument("uhash", None)

        if not action or not uhash:
            self.write({"status": "error", "msg": "Недостаточно аргументов" })
            return

        queued_manga = self.manga.get_queued_by_hash(uhash)
        if not queued_manga:
            self.write({"status": "error", "msg": "Нет у нас такой хуйни!"})
            return

        if uhash in self.mangadownload.PROCESSES:
            self.write({"status": "error", "msg": "Это URL уже обрабатывается!"})
            return

        if action in ["del"]:
            self.write({"status": "error", "msg": "Метод не реализован!" })
            return

        if action in ["add"]:
            self.mangadownload.add(queued_manga["url"], queued_manga["uiid"], queued_manga["uhash"])
            self.write({"status": "ok", "msg": "Добавлено в очередь на загрузку."})