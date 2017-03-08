# -*- coding: utf-8 -*-

from copy import copy as objcopy
import importlib
import logging
import os


IGNORE_REGISTRY = ("__init__.py", "__pycache__")


class Plugin(object):

    __description__ = ""
    __enabled__ = False
    __plugin__ = "default"

    def replicate(self):
        return objcopy(self)

    def onload(self):
        raise NotImplementedError("{}.onload()".format(__class__.__name__))

    def run(self, *args, **kwargs):
        raise NotImplementedError("{}.run()".format(__class__.__name__))


def load(path):
    names = []

    for p in os.listdir(path):
        names.append(p)

    pclasses = {}
    loaded = {}

    for addon in names:

        if addon in IGNORE_REGISTRY:
            logging.debug("Plugin %s ignored!", addon)
            continue

        if addon in pclasses:
            logging.debug("Plugin %s already loaded!", addon)
            continue

        modpath = os.path.join(path, addon.split(".", 1)[0]).replace("/", ".")

        try:
            importlib.import_module(modpath)

            for pclass in Plugin.__subclasses__():
                pclasses[pclass.__name__] = pclass

        except Exception as e:
            logging.exception("Exception: %s", e, True)

    for plugin in pclasses:

        try:

            if pclasses[plugin].__enabled__:
                loaded[pclasses[plugin].__plugin__] = pclasses[plugin]()
                loaded[pclasses[plugin].__plugin__].onload()
            else:
                logging.debug("Plugin '%s' is disabled!", pclasses[plugin].__plugin__)

        except Exception as e:
            logging.exception("In plugin: %s, %s", pclasses[plugin].__plugin__, e, True)

    return loaded
