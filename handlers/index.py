# -*- coding: utf-8 -*-

from core.util import json
import tornado.web as web
import logging


class Index(web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(Index, self).__init__(application, request)

        data = kwargs.get("data", {})
        self.db = data.get("db",  None)
        self.manga = data.get("manga",  None)
        self.users = data.get("users",  None)

    def get_usercookie(self):
        cookie = self.get_secure_cookie("dfsid", None)
        if not cookie:
            return

        return cookie.decode()

    def get(self):

        self.set_cookie("manga-cnt", str(self.manga.count))

        is_aurhorized = False

        cookie = self.get_usercookie()

        if cookie:

            if self.users.get_by_cookie(cookie):
                is_aurhorized = True

        self.render("index.tt", is_authorized=is_aurhorized, title="0/Manga: Index!")

    def post(self):
        logging.info("Request[%s] from '%s' -> '%s'", "post", self.request.remote_ip, self.request.body)

        action = self.get_argument("action", None)

        if action in ["load"]:
            articles = int(self.get_argument("articles", 10))
            offset = int(self.get_argument("offset", 0))

            data = json.dumps(self.manga.get_index_manga(articles, offset))
            self.write(data)
