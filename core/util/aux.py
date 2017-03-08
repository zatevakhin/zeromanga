# -*- coding: utf-8 -*-

import hashlib


def md5(s):
    return hashlib.md5(str(s).encode()).hexdigest()


def sha1(s):
    return hashlib.sha1(str(s).encode()).hexdigest()


def sha256(s):
    return hashlib.sha256(str(s).encode()).hexdigest()
