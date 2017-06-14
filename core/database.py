# -*- coding: utf-8 -*-

import sqlite3


class Base(object):

    __DBNAME = None

    def __init__(self, dbname):
        self.__DBNAME = dbname

    def connect(self):

        # Открываем текушую базу данные или создаем новую если ее нету
        connection = sqlite3.connect(self.__DBNAME)

        # преобразование строк таблицы в словари
        connection.row_factory = Base.dict_factory

        # текст будет типа строка, можно и bytes но требуется перекодировка
        connection.text_factory = str

        connection.execute("PRAGMA foreign_keys = ON;")
        connection.execute("PRAGMA encoding = 'UTF-8';")

        return connection

    @staticmethod
    def source(fname):
        with open(fname, "r") as f:
            return f.read()

    @staticmethod
    def dict_factory(cursor, row):
        return {col[0]: row[idx] for (idx, col) in enumerate(cursor.description)}
