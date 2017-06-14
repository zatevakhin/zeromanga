# -*- coding: utf-8 -*-

from core.util import aux
from time import time as unixtime
from core import Base


class Users(object):

    def __init__(self, data):
        self.db = data.get("db")

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

    def deauthorize_cookie(self, cookie):
        with self.db.connect() as connection:
            c = connection.cursor()
            c.execute("DELETE FROM authorized WHERE cookie = :cookie", {"cookie": cookie})
            connection.commit()

    def get_users(self, limit, offset):
        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute('''
            SELECT u.*, g.name AS group_name FROM
              users AS u JOIN groups AS g ON u.group_id = g.id
            LIMIT ? OFFSET ?;
            ''', (limit, offset)).fetchall()

    def get_group_id(self, name):
        with self.db.connect() as connection:
            c = connection.cursor()
            q = c.execute('''SELECT id FROM groups WHERE name=:name;''', {"name": str(name).lower() })
            return q.fetchone().get("id", None)

    def authorize(self, uiid, cookie, ip):
        with self.db.connect() as connection:
            c = connection.cursor()
            c.execute(Base.source("sql/authorize.sql"), (uiid, ip, cookie))
            connection.commit()

    def create_group(self, name):
        with self.db.connect() as connection:
            c = connection.cursor()
            c.execute('''INSERT INTO groups (name) VALUES (:name)''', {"name": name})
            connection.commit()

    def group_edit(self, gid, name):
        print(self, gid, name)
        with self.db.connect() as connection:
            c = connection.cursor()
            c.execute('''UPDATE groups SET name=? WHERE id=?;''', (name, gid))
            connection.commit()

    def get_groups(self):
        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute('''SELECT * FROM groups;''').fetchall()

    def select_groups(self, groups: list):
        with self.db.connect() as connection:
            c = connection.cursor()
            return c.execute(
                '''SELECT * FROM groups WHERE name in ({});'''.format(','.join('?' * len(groups))),
                groups).fetchall()


    def create_user(self, login, passwd, gid):
        with self.db.connect() as connection:
            c = connection.cursor()
            c.execute(
                '''INSERT INTO users (uhid, login, passwd, group_id) VALUES (?, ?, ?, ?)''',
                (self.make_authorization_hash(login, passwd), login, passwd, gid))
            connection.commit()

    def remove_all_user_sessions(self, uiid):
        with self.db.connect() as connection:
            c = connection.cursor()
            c.execute('''DELETE FROM authorized WHERE uiid=?;''', [uiid])
            connection.commit()

    def remove_user(self, uiid):
        self.remove_all_user_sessions(uiid)
        with self.db.connect() as connection:
            c = connection.cursor()
            c.execute('''DELETE FROM users WHERE id=?;''', [uiid])
            connection.commit()

    def remove_group(self, gid):
        with self.db.connect() as connection:
            c = connection.cursor()
            c.execute('''DELETE FROM groups WHERE id=?;''', [gid])
            connection.commit()

    def user_update(self, uiid, login, passwd, gid):
        with self.db.connect() as connection:
            c = connection.cursor()
            c.execute(
                '''UPDATE users SET uhid=?, login=?, passwd=?, group_id=? WHERE id=?;''',
                (self.make_authorization_hash(login, passwd), login, passwd, gid, uiid))
            connection.commit()
