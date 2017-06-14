# -*- coding: utf-8 -*-

import logging

from core import BaseRequestHandler


class Login(BaseRequestHandler):
    def initialize(self, data):
        super(Login, self).initialize(**data)

    def get(self):
        logging.info("Request[%s] from '%s' to '%s'", "get", self.request.remote_ip, "login")

        if self.get_current_user():
            self.redirect('/profile')
            return

        self.render("login.tt", title="0/Manga: Login!")

    def post(self):
        logging.info("Request[%s] from '%s' to '%s'", "post", self.request.remote_ip, "login")

        login = self.get_argument("zm_login", None)
        passwd = self.get_argument("zm_passwd", None)

        logging.info("Login with '%s:%s' from '%s' ip address", login, passwd, self.request.remote_ip)

        if not login:
            self.set_cookie("code", "E1")
            self.redirect("/login")
            return

        if not passwd:
            self.set_cookie("code", "E2")
            self.redirect("/login")
            return

        user = self.users.get_by_id(self.users.make_authorization_hash(login, passwd))
        if not user:
            self.set_cookie("code", "E3")
            self.redirect("/login")
            return

        cookie = self.users.make_cookie_hash(login, passwd, self.request.remote_ip)

        self.users.authorize(user["id"], cookie, self.request.remote_ip)

        self.set_secure_cookie("dfsid", cookie)

        self.redirect(self.get_argument("next", None) or '/profile')
