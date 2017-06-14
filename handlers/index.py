# -*- coding: utf-8 -*-

from core import BaseRequestHandler
from core.util import json

import logging


class Index(BaseRequestHandler):

    def initialize(self, data):
        super(Index, self).initialize(**data)
        self.manga = data.get("manga",  None)

    def get(self):
        self.set_cookie("manga-cnt", str(self.manga.count))
        self.render(
            "index.tt",
            is_authorized=bool(self.get_current_user()),
            is_allowed_access=self.allowed_access(["admins"]),
            title="0/Manga: Index!"
        )

    def post(self):
        logging.info("Request[%s] from '%s' -> '%s'", "post", self.request.remote_ip, self.request.body)

        action = self.get_argument("action", None)

        if action in ["load"]:
            articles = int(self.get_argument("articles", 10))
            offset = int(self.get_argument("offset", 0))

            data = json.dumps(self.manga.get_index_manga(articles, offset))
            self.write(data)
