# -*- coding: utf-8 -*-

from multiprocessing.dummy import Pool
from queue import Queue
import logging

from core.util.KTh import KThread
from core.util import aux
from core import plugin
from time import time

from core.mdownload import MangaDownload
from core.mcheck import MangaCheck


class TaskManager(object):

    PROCESSES = {}

    WORK_QUEUE = Queue()

    WORK_TRACK = None

    def __init__(self, data, max_workers=8):
        logging.info("Starting: '%s' with '%s' workers.", __name__, max_workers)
        self.max_workers = max_workers
        self.pool = Pool(max_workers)
        self.data = data

        self.plugins = plugin.load("core/plugins")

        self.WORK_TRACK = KThread(target=self.task_tracker)
        self.WORK_TRACK.start()

        self.initialize()

    def get_resources(self):
        return list(self.plugins.keys())

    def initialize(self):
        pass

    @property
    def db(self):
        return self.data["db"]

    @property
    def manga(self):
        return self.data["manga"]

    @property
    def storage(self):
        return self.data.get("storage")

    def add(self, ttype, **kwargs):
        self.WORK_QUEUE.put({
            "db": self.db,
            "storage": self.storage,
            "id": self.work_id(),
            "type": ttype,
            "data": kwargs
        })

    @staticmethod
    def work_id():
        return aux.sha1(str(time()))

    def get_plugin(self, name):
        logging.info("<taskman:get:plugin name='%s'>", name)
        try:
            return self.plugins[name].replicate()
        except KeyError:
            return

    def task_tracker(self):
        while True:
            task = self.WORK_QUEUE.get()
            self.pool.apply_async(
                func=self.work_make, args=[task],
                callback=self.work_complete,
                error_callback=self.work_fail
            )

    def work_make(self, work):
        logging.info("<work:make id='%s'>", work.get("id"))
        logging.info("<work:make:%s id='%s'>", work.get("type", "unknown"), work.get("id"))

        if work.get("type") in ["download", "update"]:
            md = MangaDownload(self, work)
            md.save()

            work["data"]["resource"] = md.resource
        elif work.get("type") in ["check-manga"]:
            mc = MangaCheck(work)
            mc.run()

        return work

    def work_complete(self, work):
        logging.info("<work:complete id=%s>", work.get("id"))

        if work["type"] in ["download"]:
            self.add("check-manga", mhash=work["data"]["uhash"], resource=work["data"]["resource"])

            if self.manga.get_queued_by_hash(work["data"]["uhash"]):
                logging.info("<remove:queued:manga id=%s>", work["data"]["uhash"])
                self.manga.remove_queued_by_hash(work["data"]["uhash"])

    @staticmethod
    def work_fail(*args):
        logging.info("<work:fail>", args)
