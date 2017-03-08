# -*- coding: utf-8 -*-

from urllib.parse import urlparse
import tornado.web as web


class Profile(web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(Profile, self).__init__(application, request)

        data = kwargs.get("data", {})
        self.db = data.get("db",  None)
        self.users = data.get("users",  None)
        self.manga = data.get("manga",  None)

    def get_current_user(self):
        cookie = self.get_secure_cookie("dfsid", None)

        if cookie and self.users.get_by_cookie(cookie.decode()):
            return cookie.decode()

        self.set_status(403)

    @web.authenticated
    def get(self):
        self.render("profile.tt", title="Profile:!")

    @web.authenticated
    def post(self):

        if self.get_argument("action", None) not in ["add-manga"]:
            return

        manga_url = self.get_argument("url", None)

        if not manga_url:
            return

        self.add_manga(manga_url)

    def add_manga(self, url):
        ALLOWED_RESOURCES = ["mintmanga.com", "readmanga.me"]

        if urlparse(url).netloc not in ALLOWED_RESOURCES:
            self.write({"error": "E01", "msg": "resource is not supported!"})
            return

        if self.manga.url_exists(url):
            self.write({"error": "E04", "msg": "Этот URL уже добавлен в очередь на загрузку!"})
            return

        cookie = self.get_secure_cookie("dfsid").decode()

        user = self.users.get_by_cookie(cookie)

        self.manga.add_url(user["id"], url)

        self.write({"status": "OK", "code": "G1"})
