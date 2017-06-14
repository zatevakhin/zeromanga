# -*- coding: utf-8 -*-

from core import  BaseRequestHandler
from core.util import json

from tornado import web
import logging


class UsersControl(BaseRequestHandler):

    def initialize(self, data):
        super(UsersControl, self).initialize(**data)

    @web.authenticated
    def get(self):
        logging.info("Request[%s] from '%s' to '%s'", "get", self.request.remote_ip, "adm->users")

        if not self.groups_allowed_access(["admins"]):
            return

        self.render("users.tt", title="0/Manga: Управление пользователями")

    @web.authenticated
    def post(self):
        logging.info("Request[%s] from '%s' to '%s'", "post", self.request.remote_ip, "adm->users")

        if not self.groups_allowed_access(["admins"]):
            return

        action = self.get_argument("action", None)

        if not action:
            logging.error("Unspecified action type!")
            return
        
        elif action == "get-users":
            self.write(json.dumps(self.users.get_users(100, 0)))

        elif action == "get-groups":
            self.write(json.dumps(self.users.get_groups()))

        elif action == "user-add":
            login = self.get_argument("login", None)
            passwd = self.get_argument("passwd", None)
            group = self.get_argument("group", None)

            self.users.create_user(login, passwd, group)

        elif action == "user-edit":
            uiid = self.get_argument("id", None)
            login = self.get_argument("login", None)
            passwd = self.get_argument("passwd", None)
            group = self.get_argument("group", None)

            self.users.user_update(uiid, login, passwd, group)

        elif action == "user-remove":
            uiid = self.get_argument("id", None)
            self.users.remove_user(uiid)

        elif action == "group-add":
            name = self.get_argument("name", None)
            self.users.create_group(name)

        elif action == "group-edit":
            gid = self.get_argument("id", None)
            name = self.get_argument("name", None)
            self.users.group_edit(gid, name)

        elif action == "group-remove":
            gid = self.get_argument("id", None)
            self.users.remove_group(gid)
