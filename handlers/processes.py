# -*- coding: utf-8 -*-

import tornado.web as web
import logging


class Processes(web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(Processes, self).__init__(application, request)

        data = kwargs.get("data", {})
        self.users = data.get("users",  None)

    def get_current_user(self):
        cookie = self.get_secure_cookie("dfsid", None)

        if cookie and self.users.get_by_cookie(cookie.decode()):
            return cookie.decode()

        self.set_status(403)

    @web.authenticated
    def get(self):
        self.render("processes.tt", title="0/Manga: Processes")

    @web.authenticated
    def post(self):
        print(self.request.body)
