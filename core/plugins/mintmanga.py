# -*- coding: utf-8 -*-

from core.plugin import Plugin
from core.plugins.readmanga import Readmanga


class Mintmanga(Readmanga, Plugin):
    __enabled__ = True
    __plugin__ = "mintmanga.com"

    def run(self, mode, url, mature=False):
        if mode in ["info"]:
            return self.grab_information(url)

        elif mode in ["chapters"]:
            return self.grab_chapters(url)

        elif mode in ["pages"]:
            if mature:
                url = url + "?mtr=1"
            return self.grab_pages(url)