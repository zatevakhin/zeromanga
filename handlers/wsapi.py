#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.websocket import WebSocketHandler
from core.util import json


class WebsocketAPI(WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super(WebsocketAPI, self).__init__(application, request)
        self.data = kwargs.get("data", None)
        self.users = self.data["users"]
        # self.mangadownload = self.data["mangadownload"]

    def collect_process_list(self):
        plist = {}

        # for pid, proc in self.mangadownload.PROCESSES.items():
        #     plist[pid] = proc

        return plist

    def msg(self, obj):
        self.write_message(json.dumps(obj))

    def open(self, **kwargs):
        print("WS: open", self, kwargs)

    def on_message(self, message):
        print("WS: on_message", self, message)

        print(self.collect_process_list())

        data = json.loads(message)
        if data["action"] in ["process-list"]:
            self.msg({"type": "plist", "data": self.collect_process_list()})

    def on_error(self):
        print("WS: on_error", self)

    def on_close(self):
        print("WS: on_close", self)
