# -*- coding: utf-8 -*-

from core.plugin import Plugin
from core.util import json

from html import unescape as unescapehtml
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import re


ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]

# TODO: this plugin can be optimized!

class Readmanga(Plugin):
    __version__ = "0.0.4"
    __enabled__ = True
    __plugin__ = "readmanga.me"

    def onload(self):
        print("The '{}' loaded!".format(self.__plugin__))

    @staticmethod
    def rssurl(url):
        u = urlparse(url)
        return "http://{}/rss/manga?name={}".format(u.netloc, u.path.replace("/", ""))

    @staticmethod
    def parse_mangainfo(mangainfo):
        retueninginfo = {"covers": []}

        elem_genre = mangainfo.findAll("span", {"class": "elem_genre"})
        if elem_genre:
            retueninginfo.update({"genres": list(map(lambda e: e.text.strip(", "), elem_genre))})

        elem_author = mangainfo.findAll("span", {"class": "elem_author"})
        if elem_author:
            retueninginfo.update({"authors": list(map(lambda e: e.text.strip(", "), elem_author))})

        elem_translator = mangainfo.findAll("span", {"class": "elem_translator"})
        if elem_translator:
            retueninginfo.update({"translators": list(map(lambda e: e.text.strip(", "), elem_translator))})

        elem_tag = mangainfo.findAll("span", {"class": "elem_tag"})
        if elem_tag:
            retueninginfo.update({"categories": list(map(lambda e: e.text.strip(", "), elem_tag))})

        elem_limitation = mangainfo.findAll("span", {"class": "elem_limitation"})
        if elem_limitation:
            retueninginfo.update({"rating": list(map(lambda e: e.text.strip(", "), elem_limitation))})

        elem_year = mangainfo.find("span", {"class": "elem_year"})
        if elem_year:
            retueninginfo.update({"year": elem_year.text.strip()})

        for elemp in mangainfo.findAll("p", {"class": None}):

            elem_parsed = list(map(lambda x: x.strip().lower(), elemp.text.split(":")))

            if len(elem_parsed) == 1:
                elem_parsed.append(True)

            key, value = tuple(elem_parsed)

            if key in ['томов']:
                elem_parsed = list(map(lambda x: x.strip(), value.split(",")))
                if len(elem_parsed) == 1:
                    retueninginfo.update({"volumes": value, "state": "завершена"})
                elif len(elem_parsed) == 2:
                    retueninginfo.update({"volumes": elem_parsed[0], "state": elem_parsed[1]})
                else:
                    raise ValueError

            elif key in ["перевод"]:
                retueninginfo.update({"translation": value})

            elif key in ["просмотров"]:
                retueninginfo.update({"views": value})

            elif key in ["сингл"]:
                retueninginfo.update({"single": value, "state": "завершена", "volumes": 0})

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

        info["name"] = leftcontent.find("span", attrs={"class": "name"})
        info["english"] = leftcontent.find("span", attrs={"class": "eng-name"})
        info["original"] = leftcontent.find("span", attrs={"class": "original-name"})

        for key in ["name", "english", "original"]:
            if not info[key]:
                continue

            info[key] = unescapehtml(info[key].text.strip()).strip()

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

        info["cv_count"] = len(info["covers"])

        # --------------------------------------------------------------------------
        info["translation"] = info.get("translation", None) or "завершен"

        # --------------------------------------------------------------------------
        info["rating"] = info.get("rating", None)

        # --------------------------------------------------------------------------
        info["mature"] = bool(dom.find("div", {"class": re.compile("(mature-message|mtr-message)")}))

        # --------------------------------------------------------------------------
        info["single"] = ("single" in info)

        return info

    def grab_information(self, url):
        responce = requests.get(url, timeout=10)

        if not responce:
            raise ValueError({"msg": "Can`t grab info, responce is empty!", "code": 102})

        dom = BeautifulSoup(responce.content, "lxml")
        if not dom:
            raise ValueError({"msg": "Can`t grab info, dom is empty!", "code": 102})

        return self.parse_information(dom)

    def grab_chapters(self, url):
        responce = requests.get(self.rssurl(url), timeout=10)

        if not responce:
            raise ValueError({"msg": "Can`t grab chapters, rss is empty!", "code": 103})

        dom = BeautifulSoup(responce.content, features="xml")
        if not dom:
            raise ValueError({"msg": "Can`t grab chapters, dom is empty!", "code": 103})

        chapters = []
        for index, item in enumerate(reversed(dom.rss.channel.findAll("item"))):
            title = unescapehtml(item.title.text.strip()).strip()
            chapters.append({
                "title": title,
                "url": "{}".format(item.guid.text),
                "index": (index + 1),
                "pages": [],
                "count": 0,
            })

        return chapters

    @staticmethod
    def grab_pages(url):

        responce = requests.get(url, timeout=10)

        if not responce:
            raise ValueError({"msg": "Can`t grab pages, responce is emty!", "code": 101})

        dom = BeautifulSoup(responce.content, "lxml")
        if not dom:
            raise ValueError({"msg": "Can`t grab pages, dom is emty!", "code": 101})

        script = dom.findAll("script")
        # print(script)
        match = re.findall(r"rm_h.init\([ ]?(\[\[.*\]\]),", "{}".format(dom.findAll("script")), re.I)

        if not match:
            raise ValueError({"msg": "Can`t grab pages, regex result is emty!", "code": 101})

        pages = match[0].replace('\'', '\"')

        # --------------------------------------------------------------------------
        def formaturl(obj):
            if not re.search(r"censored", obj[2], re.I):
                return "{}{}{}".format(obj[1], obj[0], obj[2])

        return list(filter(bool, map(formaturl, json.loads(pages))))

    def run(self, mode, url, mature=False):
        if mode in ["info"]:
            return self.grab_information(url)

        elif mode in ["chapters"]:
            return self.grab_chapters(url)

        elif mode in ["pages"]:
            if mature:
                url = url + "?mature=1"
            return self.grab_pages(url)
