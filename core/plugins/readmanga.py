# -*- coding: utf-8 -*-

from core.plugin import Plugin
from core.util import json
from core.util import aux


from html import unescape as unescapehtml
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import re


REPLACES = {
    "197abb66d5f8e4fcfd40e62aa31aa4d8": "single",       # Cингл
    "d367fe5fd01a11958b4dbea16999c1f5": "volumes",      # Томов
    "c0a302d44d3ea067cb671b896035db16": "views",        # Просмотров
    "a10995e0b0ee702d8db3f41c4b16319a": "translation",  # Перевод
    "a1668d871b70dcacf783eddd8be8aba9": "genres",       # Жанр
    "f9adc5f966d8810b4826f8f0c8fa9e21": "genres",       # Жанр
    "51fbd4839b8d7f367bf041695279ca59": "genres",       # Жанр
    "adee63a445a0e06b1db627103a24e266": "genres",       # Жанр
    "858a90cf2f485fd0bdedfee16822a6cc": "authors",      # Автор
    "62be86b0d01ab7128f9091a51e61ffea": "authors",      # Автор
    "3f074af16f1f0ce1afd653b6d517182d": "authors",      # Автор
    "96060b2d78295a0ce60919c57c63e66e": "authors",      # Автор
    "a99c9d8e9ea8eee4afda2ef0babfd21f": "translators",  # Переводчик
    "33fb68e54a8a415dfcafebc7ee144781": "translators",  # Переводчик
    "f71eb59870af365522fff8b5b1819204": "translators",  # Переводчик
    "2ef2250c667063c4f5a6a3bb60e8709d": "translators",  # Переводчик
    "169800f4c08a8897f21ad559c02edc31": "categories",   # Категории
    "41e20a7ec1958762ac2b46fc61ffcc97": "categories",   # Категории
    "ccb3127cf9d01ceeb65cdf236d2435fb": "categories",   # Категории
    "ac1200bb37f80a5b0eeeb35e9fc7768c": "categories",   # Категории
    "7a1fba8b0fa48ffccc4588e5187a86f9": "year",         # Год выпуска
    "1d0f627d9f2e9a557160883e1dacf9d6": "year",         # Год выпуска
    "fab3c0c32b510bfe77f70e789cac636a": "mature",       # Для взрослых
    "23ba224b81e9a0b10349487ec138d018": "rating",       # [PG] Рейтинг
    "64a617cdce261f28ad17b6f3a333ff7a": "rating",       # [PG] Рейтинг
}

ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]


class Readmanga(Plugin):
    __version__ = "0.0.3"
    __enabled__ = True
    __plugin__ = "readmanga.me"

    def onload(self):
        print("The '{}' loaded!".format(self.__plugin__))

    @staticmethod
    def rssurl(job):
        u = urlparse(job["url"])
        return "http://{}/rss/manga?name={}".format(u.netloc, u.path.replace("/", ""))

    @staticmethod
    def del_symbols(ss):
        return re.sub(r"([\\/:*?\"<>|]+|(!\[CDATA\[|\]\]))", "", ss)

    @staticmethod
    def parse_mangainfo(mangainfo):
        temporaryinfo = {}
        for elemp in mangainfo.findAll("p"):
            try:

                key = aux.md5(elemp.b.text)

                elemp.b.extract()

                temporaryinfo[key] = elemp.text.strip()

            except AttributeError:
                continue

        retueninginfo = {"name": {}, "covers": []}

        for hashkey, key in REPLACES.items():
            if hashkey not in temporaryinfo:
                continue

            retueninginfo[key] = temporaryinfo.pop(hashkey)

        return retueninginfo

    def parse_information(self, dom):

        mangainfo = dom.find("div", attrs={
            "class": re.compile("(subject-meta|mangaSettings)")
        })

        info = self.parse_mangainfo(mangainfo)

        leftcontent = dom.find("div", attrs={"class": "leftContent"})

        info["description"] = leftcontent.find("meta", attrs={
            "itemprop": re.compile("description")
        }).get("content", "")

        info["name"]["ru"] = leftcontent.find("span", attrs={"class": "name"})
        info["name"]["en"] = leftcontent.find("span", attrs={"class": "eng-name"})
        info["name"]["ja"] = leftcontent.find("span", attrs={"class": "original-name"})

        # --------------------------------------------------------------------------
        if info["name"]["ru"]:
            info["name"]["ru"] = self.del_symbols(unescapehtml(
                info["name"]["ru"].text.strip()
            )).strip()

        # --------------------------------------------------------------------------
        if info["name"]["en"]:
            info["name"]["en"] = self.del_symbols(unescapehtml(
                info["name"]["en"].text.strip()
            )).strip()

        # --------------------------------------------------------------------------
        if info["name"]["ja"]:
            info["name"]["ja"] = self.del_symbols(unescapehtml(
                info["name"]["ja"].text.strip()
            )).strip()

        titles = [info["name"]["ru"], info["name"]["en"], info["name"]["ja"]]
        info["title"] = list(filter(bool, titles))[0]

        # --------------------------------------------------------------------------
        covers = dom.find("div", attrs={"class": "picture-fotorama"})

        # --------------------------------------------------------------------------
        for index, image in enumerate(covers.findAll(re.compile("img|a"))):
            if image.name not in ["img", "a"]:
                continue

            if not image.get("data-full", None):
                continue

            imurl = [image.get("href", None), image.get("src", None)]

            imurl = list(filter(lambda x: x.split(".")[-1] in ALLOWED_EXTENSIONS, filter(bool, imurl)))

            info["covers"].append(imurl[0])

        # --------------------------------------------------------------------------------------------------------------
        if "volumes" in info:
            volme_state = str(info["volumes"]).split(",")
            # ------------------------------------------------------------------------
            if len(volme_state) == 1:
                info["volumes"] = int(volme_state[0].strip())
                info["state"] = "завершена"

            # ------------------------------------------------------------------------
            if len(volme_state) == 2:
                info["volumes"] = int(volme_state[0].strip())
                info["state"] = volme_state[1].strip()
        else:
            info["volumes"] = 0

        # --------------------------------------------------------------------------
        if "genres" in info:
            info["genres"] = str(info["genres"]).replace("\u2026", "").split(",")
            info["genres"] = list(map((lambda x: x.strip()), info["genres"]))

        # --------------------------------------------------------------------------
        if "categories" in info:
            info["categories"] = str(info["categories"]).split(",")
            info["categories"] = list(map((lambda x: x.strip()), info["categories"]))
        else:
            info["categories"] = []

        # --------------------------------------------------------------------------
        if "authors" in info:
            info["authors"] = str(info["authors"]).split(",")
            info["authors"] = list(map(lambda x: x.strip(), info["authors"]))

        # --------------------------------------------------------------------------
        if "translators" in info:
            info["translators"] = str(info["translators"]).replace("\u2026", "").split(",")
            info["translators"] = list(map(lambda x: x.strip(), info["translators"]))

        # --------------------------------------------------------------------------
        info["translation"] = info.get("translation", None) or "завершен"

        # --------------------------------------------------------------------------
        info["rating"] = info.get("rating", None)

        # --------------------------------------------------------------------------
        info["mature"] = ("mature" in info)

        # --------------------------------------------------------------------------
        info["single"] = ("single" in info)

        return info

    def grab_information(self):
        responce = requests.get(self.job["url"], timeout=2)

        if not responce:
            raise Exception("Responce is empty!")

        dom = BeautifulSoup(responce.content, "lxml")
        if not dom:
            raise Exception("Can`t build dom tree!")

        return self.parse_information(dom)

    def grab_chapters(self):
        self.job["rssurl"] = self.rssurl(self.job)
        print(self.job["rssurl"])
        responce = requests.get(self.job["rssurl"], timeout=2)

        if not responce:
            raise Exception("Responce from rss is empty!")

        dom = BeautifulSoup(responce.content, features="xml")
        if not dom:
            raise Exception("Can`t build dom tree!")

        manga = {"chapters": []}
        for index, item in enumerate(reversed(dom.rss.channel.findAll("item"))):
            chapt = self.del_symbols(unescapehtml(item.title.text.strip())).strip()
            manga["chapters"].append({
                "chapt": chapt,
                "url": "{}".format(item.guid.text),
                "index": (index + 1),
                "pages": [],
                "count": 0,
            })

        manga["chapterscount"] = len(manga["chapters"])

        return manga

    @staticmethod
    def grab_pages(chapter):

        responce = requests.get(chapter["url"], timeout=2)

        if not responce:
            raise Exception("Responce is empty!")

        dom = BeautifulSoup(responce.content, "lxml")
        if not dom:
            raise Exception("Can`t build dom tree!")

        match = re.findall(r"rm_h.init\([ ]?(\[\[.*\]\]),", "{}".format(dom.findAll("script")), re.I)

        pages = match[0].replace('\'', '\"')

        # --------------------------------------------------------------------------
        def formaturl(obj):
            if not re.search(r"censored", obj[2], re.I):
                return "{}{}{}".format(obj[1], obj[0], obj[2])

        return list(filter(bool, map(formaturl, json.loads(pages))))

    def run(self, job):
        self.job = job

        return {
            **self.grab_information(),
            **self.grab_chapters()
        }
