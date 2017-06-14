# -*- coding: utf-8 -*-

from core import Base
import logging
import os


class Install(object):

    def __init__(self, data):
        self.db = data.get("db")
        self.users = data.get("users")
        self.storage = data.get("storage")

    def run_install(self):
        logging.info(":: Запущенна процедура установки ::")

        logging.info("  ==> Создание папок")
        self.create_folders()

        logging.info("  ==> Создание таблиц")
        self.create_tables()

        logging.info("  ==> Добавление групп по умолчанию в базу данных.")
        self.create_groups()

        logging.info("  ==> Добавление пользователей по умолчанию в базу данных.")
        self.create_users()

    def create_folders(self):
        if not os.path.exists(self.storage):
            logging.info("    --> Создание папки хранилища.")
            os.mkdir(self.storage)

    def create_tables(self):
        connection = self.db.connect()

        c = connection.cursor()
        c.executescript(Base.source("sql/create_tables.sql"))

        connection.commit()
        connection.close()

    def create_groups(self):
        logging.info("    --> Добавление группы 'администраторы'.")
        self.users.create_group('admins')

        logging.info("    --> Добавление группы 'пользователи'.")
        self.users.create_group('users')

    def create_users(self):
        logging.info("    --> Получение идентификатора группы 'администраторы'.")
        gid = self.users.get_group_id('admins')

        logging.info("    --> создание 'администратора' имя: root, пароль: r00t, gid: %s.", gid)
        self.users.create_user('root', 'r00t', gid)
