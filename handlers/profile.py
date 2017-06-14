# -*- coding: utf-8 -*-

from core import BaseRequestHandler
from tornado import web


class Profile(BaseRequestHandler):

    def initialize(self, data):
        super(Profile, self).initialize(**data)

    @web.authenticated
    def get(self):
        self.render(
            "profile.tt",
            is_allowed_access=self.allowed_access(["admins"]),
            title="0/Manga: Profile"
        )
