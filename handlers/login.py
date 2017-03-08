# -*- coding: utf-8 -*-

from tornado import template
from tornado import web
import logging

class User(object):

    def __init__(self, login, passwd, ip, cookie):
        self.cookie = cookie
        self.passwd = passwd
        self.login = login
        self.ip = ip


class Login(web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(Login, self).__init__(application, request)

        data = kwargs.get("data", {})
        self.db = data.get("db", None)
        self.users = data.get("users", None)

    def get(self):
        logging.info("Request[%s] from '%s' to '%s'", "get", self.request.remote_ip, "login")

        cookie = self.get_secure_cookie("dfsid", None)

        if cookie and self.users.get_by_cookie(cookie.decode()):
            self.redirect('/profile')
            return

        self.render("login.tt", title="0/Manga: Login!")

    def post(self):
        logging.info("Request[%s] from '%s' to '%s'", "post", self.request.remote_ip, "login")

        login = self.get_argument("xloginx", None)
        passw = self.get_argument("xpasswx", None)

        logging.info("Login with '%s:%s' from '%s' ip address", login, passw, self.request.remote_ip)

        if not (login or passw):
            self.set_cookie("ecode", "0x01")
            self.redirect("/login")
            return

        userrow = self.users.get_by_id(self.users.make_authorization_hash(login, passw))
        if not userrow:
            self.set_cookie("ecode", "0x02")
            self.redirect("/login")
            return

        cookie = self.users.make_cookie_hash(login, passw, self.request.remote_ip)

        self.users.authorize(userrow["id"], cookie, self.request.remote_ip)

        self.set_secure_cookie("dfsid", cookie)

        self.redirect(self.get_argument("next", None) or '/profile')
