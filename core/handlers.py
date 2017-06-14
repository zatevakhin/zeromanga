# -*- coding: utf-8 -*-

from core.users import Users
from tornado import web
import os


class BaseRequestHandler(web.RequestHandler):

    def initialize(self, **kwargs):
        self.users = kwargs.get("users", None)  # type: Users

    def get_user_cookie(self):
        cookie = self.get_secure_cookie("dfsid")
        if cookie:
            return cookie.decode()

    def get_userdata(self):
        cookie = self.get_user_cookie()
        if cookie:
            return self.users.get_by_cookie(cookie)

    def allowed_access(self, groups: list) -> bool:
        user = self.get_userdata()
        if user:
            return user.get("group_id", 0) in map(lambda x: x["id"], self.users.select_groups(groups))

    def groups_allowed_access(self, groups: list) -> bool:
        if self.allowed_access(groups):
            return True

        self.set_status(403)
        self.write_error(403)

    def get_current_user(self) -> str:
        cookie = self.get_user_cookie()

        if cookie:
            if self.users.get_by_cookie(cookie):
                return cookie

        self.clear_cookie("dfsid")

    def writef(self, fname, content_type, buffsz=4096):
        file_sz = os.path.getsize(fname)
        self.set_header('Content-Type', content_type)
        self.set_header('Content-Length', file_sz)

        with open(fname, 'rb') as f:
            while True:
                data = f.read(buffsz)

                if not data:
                    break

                self.write(data)

        self.finish()