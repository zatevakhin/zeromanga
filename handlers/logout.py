# -*- coding: utf-8 -*-

from core import BaseRequestHandler
from tornado import web


class Logout(BaseRequestHandler):

    def initialize(self, data):
        super(Logout, self).initialize(**data)

    @web.authenticated
    def get(self):
        cookie = self.get_user_cookie()
        self.users.deauthorize_cookie(cookie)
        self.redirect('/')
