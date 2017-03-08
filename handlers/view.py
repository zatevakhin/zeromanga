# -*- coding: utf-8 -*-

from urllib.parse import urlparse
from core.database import Base
import tornado.web as web
import re

class View(web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(View, self).__init__(application, request)
        data = kwargs.get("data", {})
        self.db = data.get("db", None)
        self.manga = data.get("manga", None)
        self.users = data.get("users", None)

    def get_usercookie(self):
        cookie = self.get_secure_cookie("dfsid", None)
        if not cookie:
            return

        return cookie.decode()

    def get_userdata(self):
        cookie = self.get_usercookie()

        if not cookie:
            return

        user = self.users.get_by_cookie(cookie)

        if not user:
            return

        return user

    def get(self, mangaid):

        manga = self.manga.get_manga_full(mangaid)

        manga["resource"] = urlparse(manga["url"]).netloc

        manga["chapters"].sort(key=(lambda x: x['index']))

        user = self.get_userdata()

        if user:

            with self.db.connect() as connection:

                c = connection.cursor()

                for chapter in manga["chapters"]:
                    # TODO: сделать подсчет прочитаных на стороне бд.
                    items = c.execute(Base.source("sql/select_readed.sql"), {
                        "ciid": chapter['id'],
                        "miid": manga['id'],
                        "uiid": user['id']
                    }).fetchall()

                    chapter["readed"] = len(items)
        else:
            self.clear_cookie("dfsid")

        ua = self.request.headers["user-agent"]
        if re.search("(android)", ua, re.I):
            self.render("view.mobile.tt", manga=manga, title=manga["title"])
        else:
            self.render("view.tt", manga=manga, title=manga["title"])


    def post(self, mangaid):

        action = self.get_argument("action", None)

        if action in ["get.thumbnails"]:
            chash = self.get_argument("chash", None)

            chapter = self.manga.get_manga_chapt(mangaid, chash)

            user = self.get_userdata()

            if user:
                with self.db.connect() as connection:
                    c = connection.cursor()
                    items = c.execute(Base.source("sql/select_readed.sql"), {
                        "miid": chapter['mangaid'],
                        "ciid": chapter['id'],
                        "uiid": user['id']
                    }).fetchall()

                    chapter["readed"] = [item['pageid'] for item in items]
            else:
                self.clear_cookie("dfsid")

            self.write(chapter)
