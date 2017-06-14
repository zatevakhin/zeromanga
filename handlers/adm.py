# -*- coding: utf-8 -*-

from core import BaseRequestHandler
from tornado import web


class AdminArea(BaseRequestHandler):

    def initialize(self, data):
        super(AdminArea, self).initialize(**data)

    @web.authenticated
    def get(self):
        if not self.groups_allowed_access(["admins"]):
            return

        self.render("adm.tt", title="0/Manga: Admin Panel")

    @web.authenticated
    def post(self):
        if not self.groups_allowed_access(["admins"]):
            return

        print(self.request.body)
