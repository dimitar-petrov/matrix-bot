#!/usr/bin/env python
import json
import logging as log


class MatrixConfig(object):
    URL = "url"
    USR = "user_id"
    TOK = "token"
    PWD = "password"
    ADM = "admins"
    CIS = "case_insensitive"
    PLG = "plugins"
    SSL = "cert_verify"
    json = {}
    rooms = {}

    def __init__(self, json, conf_location):
        self.conf_location = conf_location
        self.json = json

    @classmethod
    def from_file(cls, f):
        j = json.load(f)

        # defaults

        if 'cert_verify' not in j:
            j['cert_verify'] = True

        if 'any_can_invite' not in j:
            j['any_can_invite'] = False

        if 'admins' not in j:
            j['any_can_invite'] = True
        elif len(j['admins']) == 0:
            j['any_can_invite'] = True

        if 'plugins' not in j:
            j['plugins'] = ['config']

        return MatrixConfig(j, f.name)

    def save(self):
        with open(self.conf_location, 'w') as f:
            f.write(json.dumps(self.json, indent=4))

    def set(self, key, val):
        log.debug("Set config parameter %s to value %r" % (key, val))
        self.json[key] = val

    def get(self, key):
        self.json.get(key)
