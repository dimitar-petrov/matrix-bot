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

    def __init__(
        self, hs_url, user_id, password, admins,
        case_insensitive, conf_location, access_token=None,
        plugins=[], ssl_verify=True
    ):
        self.conf_location = conf_location
        self.json = {
            MatrixConfig.URL: hs_url,
            MatrixConfig.TOK: access_token,
            MatrixConfig.USR: user_id,
            MatrixConfig.PWD: password,
            MatrixConfig.ADM: admins,
            MatrixConfig.CIS: case_insensitive,
            MatrixConfig.PLG: plugins,
            MatrixConfig.SSL: ssl_verify,
        }

    @classmethod
    def from_file(cls, f):
        j = json.load(f)

        if MatrixConfig.TOK not in j:
            token = None
        else:
            token = j[MatrixConfig.TOK]

        if MatrixConfig.PLG not in j:
            plugins = None
        else:
            plugins = j[MatrixConfig.PLG]

        if MatrixConfig.SSL not in j:
            ssl_verify = True
        else:
            ssl_verify = j[MatrixConfig.SSL]

        return MatrixConfig(
            hs_url=j[MatrixConfig.URL],
            user_id=j[MatrixConfig.USR],
            access_token=token,
            password=j[MatrixConfig.PWD],
            admins=j[MatrixConfig.ADM],
            case_insensitive=j[MatrixConfig.CIS] if MatrixConfig.CIS in j else False,
            conf_location=f.name,
            plugins=plugins,
            ssl_verify=ssl_verify,
        )

    def save(self):
        with open(self.conf_location, 'w') as f:
            f.write(json.dumps(self.json, indent=4))

    def set(self, key, val):
        log.debug("Set config parameter %s to value %r" % (key, val))
        self.json[key] = val

    def get(self, key):
        self.json.get(key)
