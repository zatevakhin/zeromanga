# -*- coding: utf-8 -*-

from base64 import b64decode
from core.util import json
from tornado import web
import logging
import re

from core.database import Base


class Search(web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(Search, self).__init__(application, request)

        data = kwargs.get("data", {})
        self.db = data.get("db", None)
        self.users = data.get("users", None)
        self.manga = data.get("manga", None)

    def get(self):
        logging.info("Request[%s] from '%s' to '%s'", "get", self.request.remote_ip, "search")

        search = {"genres": []}
        with self.db.connect() as connection:
            c = connection.cursor()
            search["genres"] = c.execute('''SELECT * FROM genres;''').fetchall() or []

        self.render("search.tt", title="0/Manga: Search!", search=search)

    def post(self):
        logging.info("Request[%s] from '%s' to '%s'", "post", self.request.remote_ip, "search")

        action = self.get_argument("action", None)

        if action in ['search']:
            self.search()

    def search(self):
        data = self.get_argument("data", None)

        if not data:
            self.write({"status": "error", "msg": "data is emty!"})
            return

        if not json.isjson(data):
            self.write({"status": "error", "msg": "data is not json!"})
            return

        data = json.loads(data)

        data["genres"]["include"] = list(filter(int, data["genres"]["include"]))
        data["genres"]["exclude"] = list(filter(int, data["genres"]["exclude"]))

        arr = [*data["genres"]["include"], *data["genres"]["exclude"]]
        query = Base.source("sql/search.sql")
        query = query.format(
            ",".join("?" * len(data["genres"]["include"])),
            ",".join("?" * len(data["genres"]["exclude"]))
        )

        result = []
        with self.db.connect() as connection:
            c = connection.cursor()
            result = c.execute(query, arr).fetchall()

            if data["text"]:
                result = list(filter(lambda x: re.search(data["text"], x["search"], re.I), result))

            for row in result:
                row.update({"title": (row["name"] or row["english"] or row["original"])})
                del row["search"]

        self.write({"request": data, "result": result})
