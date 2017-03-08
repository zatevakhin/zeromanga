# -*- coding: utf-8 -*-

from core.util import aux
from time import time as unixtime
from core import Base

class Users(object):

    def __init__(self, data):
        self.db = data.get("db")

        # TODO: При создани класса проводить очистку старых пользовательских сессий.

    @staticmethod
    def make_cookie_hash(login, passwd, ip):
        return aux.sha1("{}:{}:{}:{}".format(login, passwd, ip, unixtime()))

    @staticmethod
    def make_authorization_hash(login, passwd):
        return aux.sha1("{}:{}".format(login, passwd))

    def get_by_id(self, uhid):

        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute('''SELECT * FROM `users` WHERE `uhid` == :uhid LIMIT 1''', {'uhid': uhid}).fetchone()

    def get_by_cookie(self, cookie):

        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute(Base.source("sql/user_by_cookie.sql"), {'cookie': cookie}).fetchone()


    # def is_authorized(self):
    #     # При попытке логина тоже проводить очистку сессий.
    #
    #     with self.db.connect() as connection:
    #         c = connection.cursor()
    #
    #         c.execute(Base.source("sql/is_authorized.sql"))

    def authorize(self, uiid, cookie, ip):
        with self.db.connect() as connection:
            c = connection.cursor()
            c.execute(Base.source("sql/authorize.sql"), (uiid, ip, cookie))
            connection.commit()
