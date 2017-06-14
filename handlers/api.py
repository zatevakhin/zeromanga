# -*- coding: utf-8 -*-

from core import BaseRequestHandler
from core import TaskManager
from core import Manga
from core import Base
from core.util import aux

from tornado import web
import logging
import shutil
import os


class API(BaseRequestHandler):
    TASKMAN = None

    def initialize(self, data):
        super(API, self).initialize(**data)
        self.TASKMAN = data.get("taskman", None)  # type: TaskManager
        self.manga = data.get("manga", None)  # type: Manga
        self.db = data.get("db", None)  # type: Base
        self.storage = data.get("storage")

    @web.authenticated
    def post(self):

        action = self.get_argument("action", None)

        if action in ['remove-manga']:

            if not self.allowed_access(["admins"]):
                self.write({"status": "error", "msg": "You don`t have permission for this action!"})
                self.set_status(403)
                return

            mhash = self.get_argument("mhash", None)

            if not mhash:
                self.write({"status": "error", "msg": "Not enough arguments!"})
                return

            try:
                self.manga_remove(mhash)
            except Exception:
                self.write({"status": "error", "msg": "Error, see server log!"})
                logging.error("In %s.post()\n%s", __class__, aux.exception())

        elif action in ['update-manga']:
            if not self.allowed_access(["admins"]):
                self.write({"status": "error", "msg": "You don`t have permission for this action!"})
                self.set_status(403)
                return

            mhash = self.get_argument("mhash", None)

            if not mhash:
                self.write({"status": "error", "msg": "Not enough arguments!"})
                return

            try:
                self.manga_update(mhash)
            except Exception:
                self.write({"status": "error", "msg": "Error, see server log!"})
                logging.error("In %s.post()\n%s", __class__, aux.exception())

        else:
            self.write({"status": "error", "msg": "Unknown action!"})

    def manga_update(self, mhash):
        manga = self.manga.get_manga_by_hash(mhash)

        if not manga:
            self.write({"status": "error", "msg": "Manga not found in data base!"})
            return

        self.write({"status": "ok", "msg": "Manga ({}), update started!".format(manga["name"])})
        self.TASKMAN.add("update", uhash=mhash, resource=manga["resource"], url=manga["url"])

    def manga_remove(self, mhash):
        manga = self.manga.get_manga_by_hash(mhash)

        if not manga:
            self.write({"status": "error", "msg": "Manga not found in data base!"})
            return

        logging.warning("Removing manga (%s)", manga["name"])

        with self.db.connect() as connection:
            c = connection.cursor()
            logging.warning("    (db) DELETE FROM uread WHERE mangaid = %s", manga["id"])
            c.execute("""DELETE FROM uread WHERE mangaid = :miid""", {"miid": manga["id"]})

            logging.warning("    (db) DELETE FROM chapters WHERE mangaid = %s", manga["id"])
            c.execute("""DELETE FROM chapters WHERE mangaid = :miid""", {"miid": manga["id"]})

            logging.warning("    (db) DELETE FROM manga_genres WHERE manga_id = %s", manga["id"])
            c.execute("""DELETE FROM manga_genres WHERE manga_id = :miid""", {"miid": manga["id"]})

            logging.warning("    (db) DELETE FROM manga_authors WHERE manga_id = %s", manga["id"])
            c.execute("""DELETE FROM manga_authors WHERE manga_id = :miid""", {"miid": manga["id"]})

            logging.warning("    (db) DELETE FROM manga_translators WHERE manga_id = %s", manga["id"])
            c.execute("""DELETE FROM manga_translators WHERE manga_id = :miid""", {"miid": manga["id"]})

            logging.warning("    (db) DELETE FROM manga WHERE id = %s", manga["id"])
            c.execute("""DELETE FROM manga WHERE id = :miid""", {"miid": manga["id"]})
            connection.commit()

        manga_storage = os.path.join(self.storage, manga["resource"], manga["mhash"])

        if not os.path.exists(manga_storage):
            logging.warning("Manga (%s) folder not found!", manga["name"])
            self.write({"status": "error", "msg": "Manga folder not found!"})
            return

        logging.warning("    (fs) rm -rf %s", manga_storage)
        shutil.rmtree(manga_storage)

        self.write({"status": "ok", "msg": "Manga ({}) completly deleted!".format(manga["name"])})
