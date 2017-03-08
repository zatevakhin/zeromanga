# -*- coding: utf-8 -*-

from json import loads
from json import load

from json import dumps
from json import dump


def isjson(s):
  try:
    return bool(loads(s, strict=False))
  except Exception:
    return
