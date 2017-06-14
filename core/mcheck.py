# -*- coding: utf-8 -*-

from core.util import json
import logging
import shutil
import os


class MangaCheck(object):

    def __init__(self, work):
        self.work = work

    @property
    def db(self):
        return self.work["db"]

    @property
    def storage(self):
        return self.work["storage"]

    @property
    def mhash(self):
        return self.work["data"]["mhash"]

    @property
    def resource(self):
        return self.work["data"]["resource"]

    @property
    def info(self):
        path = os.path.join(self.storage, self.resource, self.mhash, ".meta", "info.json")
        if not os.path.exists(path):
            return

        with open(path, "r") as f:
            return json.load(f)

    def get_manga_chapters(self):
        with self.db.connect() as connection:
            c = connection.execute("""
                SELECT chash FROM
                  manga    AS m JOIN
                  chapters AS c ON m.id = c.mangaid
                WHERE m.mhash = :mhash""", {"mhash": self.mhash})

            return list(map(lambda x: x["chash"], c.fetchall() or []))

    def get_ciid(self, chash):
        with self.db.connect() as connection:
            return connection.execute("""SELECT id FROM chapters WHERE chash = :chash""", {
                "chash": chash
            }).fetchone().get("id", None)

    def fix_difference(self, difference):
        logging.warning("Found difference in [%s/%s]: %s", self.resource, self.mhash, difference)
        ciids = list(filter(bool, map(lambda x: self.get_ciid(x), difference)))

        self.fix_db_difference(ciids)
        self.fix_fs_difference(difference)

    def fix_db_difference(self, ciids):
        logging.warning("Removing from table 'chapters,uread' rows with chapter ids %s", ciids)

        with self.db.connect() as connection:
            c = connection.cursor()
            for ciid in ciids:
                logging.warning("    -> rm (%s:%s)", self.mhash, ciid)
                c.execute("""DELETE FROM uread WHERE chaptid = :ciid""", {"ciid": ciid})
                c.execute("""DELETE FROM chapters WHERE id = :ciid""", {"ciid": ciid})

            connection.commit()

    def fix_fs_difference(self, difference):
        logging.warning("Removing from fs chapters with chash`s %s", difference)
        lst = list(map(lambda x: os.path.join(self.storage, self.resource, self.mhash, x), difference))
        lst += list(map(lambda x: os.path.join(self.storage, self.resource, self.mhash, ".meta", "t", x), difference))

        for path in filter(lambda x: os.path.exists(x), lst):
            logging.warning("    -> rm -r (%s)", path)
            shutil.rmtree(path)

    def run(self):
        info = self.info

        if not info:
            logging.error("In %s.run(). Info not found!", __class__)
            return

        chapters = info.get("chapters", [])

        if not chapters:
            logging.error("In %s.run(). In info chapters not found!", __class__)
            return

        in_chashs = list(map(lambda x: x["chash"], chapters))
        db_chashs = self.get_manga_chapters()

        if not db_chashs:
            logging.error("In %s.run(). In manga '%s/%s' chapters not found!", __class__, self.resource, self.mhash)
            return

        difference = list(set(db_chashs).difference(in_chashs))

        if not difference:
            logging.info("In %s.run(). Check complete manga is ok.", __class__)
            return

        logging.error("In %s.run(). In manga '%s/%s' Found difference try to fix!",
                      __class__, self.resource, self.mhash)

        self.fix_difference(difference)
