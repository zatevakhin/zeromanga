# -*- coding: utf-8 -*-

from core.plugin import Plugin
from core.plugins.readmanga import Readmanga


class Mintmanga(Readmanga, Plugin):
    __enabled__ = True
    __plugin__ = "mintmanga.com"
