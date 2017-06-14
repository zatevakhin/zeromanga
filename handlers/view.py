# -*- coding: utf-8 -*-

from core import BaseRequestHandler
from core.database import Base

from core import MangaItem
import re


class View(BaseRequestHandler):

    def initialize(self, data):
        super(View, self).initialize(**data)
        self.db = data.get("db", None)  # type: Base

    def get(self, mangaid):
        miteme = MangaItem(self.db, mangaid)

        user = self.get_userdata()

        ua = self.request.headers["user-agent"]
        if re.search("(android)", ua, re.I):
            self.render("view.mobile.tt", manga=miteme, user=user, title=miteme.title)
            return

        self.render(
            "view.tt",
            manga=miteme,
            user=user,
            title=miteme.title,
            is_allowed_access = self.allowed_access(["admins"]),
        )

    def post(self, mangaid):

        action = self.get_argument("action", None)

        if action in ["get.thumbnails"]:
            chash = self.get_argument("chash", None)

            miteme = MangaItem(self.db, mangaid)
            chapter = miteme.get_chapter(chash)

            user = self.get_userdata()

            if user:
                chapter["readed"] = miteme.get_readed(chapter["id"], user["id"])
            else:
                self.clear_cookie("dfsid")

            self.write(chapter)
