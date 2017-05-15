#!/usr/bin/env python
import json
import logging as log


class MatrixConfig(object):
    URL = "url"
    USR = "user"
    TOK = "token"
    PWD = "password"
    ADM = "admins"
    CIS = "case_insensitive"
    PLG = "plugins"
    SSL = "cert_verify"

    def __init__(self, hs_url, user_id, password, admins, case_insensitive, conf_location, access_token=None, plugins=[], ssl_verify=True):
        self.user_id = user_id
        self.password = password
        self.base_url = hs_url
        self.admins = admins
        self.token = access_token
        self.case_insensitive = case_insensitive
        self.conf_location = conf_location
        self.plugins = plugins
        self.ssl_verify = ssl_verify

    @classmethod
    def to_file(cls, config, f):
        f.write(json.dumps({
            MatrixConfig.URL: config.base_url,
            MatrixConfig.TOK: config.token,
            MatrixConfig.USR: config.user_id,
            MatrixConfig.PWD: config.password,
            MatrixConfig.ADM: config.admins,
            MatrixConfig.CIS: config.case_insensitive
        }, indent=4))

    @classmethod
    def from_file(cls, f):
        j = json.load(f)

        # convert old 0.0.1 matrix-python-sdk urls to 0.0.3+
        hs_url = j[MatrixConfig.URL]
        if hs_url.endswith("/_matrix/client/api/v1"):
            hs_url = hs_url[:-22]
            log.info("Detected legacy URL, using '%s' instead. Consider changing this in your configuration." % hs_url)

        if not MatrixConfig.TOK in j:
            token = None
        else:
            token = j[MatrixConfig.TOK]

        if not MatrixConfig.PLG in j:
            plugins = None
        else:
            plugins = j[MatrixConfig.PLG]

        if not MatrixConfig.SSL in j:
            ssl_verify = True
        else:
            ssl_verify = j[MatrixConfig.SSL]

        return MatrixConfig(
            hs_url=hs_url,
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
            f.write(json.dumps({
                MatrixConfig.URL: self.base_url,
                MatrixConfig.TOK: self.token,
                MatrixConfig.USR: self.user_id,
                MatrixConfig.PWD: self.password,
                MatrixConfig.ADM: self.admins,
                MatrixConfig.CIS: self.case_insensitive,
                MatrixConfig.PLG: self.plugins,
                MatrixConfig.SSL: self.ssl_verify,
            }, indent=4))
