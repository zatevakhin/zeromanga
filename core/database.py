# -*- coding: utf-8 -*-

import sqlite3


class Base(object):

    __DBNAME = None

    def __init__(self, dbname):
        self.__DBNAME = dbname

        # открываем бд
        connection = self.connect()

        c = connection.cursor()

        c.executescript(Base.source("sql/create_tables.sql"))

        # Записываем данные из кеша
        connection.commit()

        # Закрываем соединение
        connection.close()

    def connect(self):

        # Открываем текушую базу данные или создаем новую если ее нету
        connection = sqlite3.connect(self.__DBNAME)

        # преобразование строк таблицы в словари
        connection.row_factory = Base.dict_factory

        # текст будет типа строка, можно и bytes но требуется перекодировка
        connection.text_factory = str

        #
        connection.execute("PRAGMA foreign_keys = ON;")

        return connection

    @staticmethod
    def source(fname):
        with open(fname, "r") as f:
            return f.read()

    @staticmethod
    def make(fname, data):
        q = Base.source(fname)
        for item in data:
            q = q.replace((":%s" % item), ("%s" % data[item]))
        return q


    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
