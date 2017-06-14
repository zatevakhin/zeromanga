# -*- coding: utf-8 -*-

from core import BaseRequestHandler
from tornado import web


class Processes(BaseRequestHandler):

    def initialize(self, data):
        super(Processes, self).initialize(**data)

    @web.authenticated
    def get(self):

        if not self.groups_allowed_access(["admins"]):
            return

        self.render("processes.tt", title="0/Manga: Processes")

    @web.authenticated
    def post(self):

        if not self.groups_allowed_access(["admins"]):
            return

        print(self.request.body)
