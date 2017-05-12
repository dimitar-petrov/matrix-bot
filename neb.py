#!/usr/bin/env python
import argparse

from matrix_client.api import MatrixHttpApi
from neb.engine import Engine
from neb.matrix import MatrixConfig
from plugins.b64 import Base64Plugin
from plugins.guess_number import GuessNumberPlugin
from plugins.jenkins import JenkinsPlugin
from plugins.jira import JiraPlugin
from plugins.url import UrlPlugin
from plugins.time_utils import TimePlugin
from plugins.github import GithubPlugin
from plugins.google import GooglePlugin
from plugins.prometheus import PrometheusPlugin

import logging
import logging.handlers
import time

log = logging.getLogger(name=__name__)

# TODO:
# - Add utility plugins in neb package to do things like "invite x to room y"?
# - Add other plugins as tests of plugin architecture (e.g. anagrams, dictionary lookup, etc)


def generate_config(url, username, password, admin, config_loc):
    config = MatrixConfig(
            hs_url=url,
            user_id=username,
            password=password,
            admins=[admin],
            case_insensitive=False,
            conf_location=config_loc
    )
    print config_loc
    config.save()
    return config



def load_config(loc):
    try:
        with open(loc, 'r') as f:
            return MatrixConfig.from_file(f)
    except:
        pass


def configure_logging(logfile):
    log_format = "%(asctime)s %(levelname)s: %(message)s"
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format
    )

    if logfile:
        formatter = logging.Formatter(log_format)

        # rotate logs (20MB, max 6 = 120MB)
        handler = logging.handlers.RotatingFileHandler(
              logfile, maxBytes=(1000 * 1000 * 20), backupCount=5)
        handler.setFormatter(formatter)
        logging.getLogger('').addHandler(handler)


def main(config):
    # setup api/endpoint
    if not config.token:
        matrix = MatrixHttpApi(config.base_url)
        res = matrix.login(login_type="m.login.password", user="neb", password="G@h0km<0n@")
        log.debug("Login result: %r" % res)
        config.token = res["access_token"]
        config.save()
        matrix.token = config.token
    else:
        matrix = MatrixHttpApi(config.base_url, config.token)


    log.debug("Setting up plugins...")
    plugins = [
        TimePlugin,
        Base64Plugin,
        GuessNumberPlugin,
        GooglePlugin,
        #JiraPlugin,
        #UrlPlugin,
        #GithubPlugin,
        #JenkinsPlugin,
        #PrometheusPlugin,
    ]

    # setup engine
    engine = Engine(matrix, config)
    for plugin in plugins:
        engine.add_plugin(plugin)

    engine.setup()

    while True:
        try:
            log.info("Listening for incoming events.")
            engine.event_loop()
        except Exception as e:
            log.error("Ruh roh: %s", e)
        time.sleep(5)

    log.info("Terminating.")


if __name__ == '__main__':
    a = argparse.ArgumentParser("Runs NEB. See plugins for commands.")
    a.add_argument(
        "-c", "--config", dest="config",
        help="The config to create or read from."
    )
    a.add_argument(
        "-l", "--log-file", dest="log",
        help="Log to this file."
    )
    args = a.parse_args()

    configure_logging(args.log)
    log.info("  ===== NEB initialising ===== ")

    config = None
    if args.config:
        log.info("Loading config from %s", args.config)
        config = load_config(args.config)
        log.info("Config %r", config)
        if not config:
            log.info("Setting up for an existing account.")
            print "Config file could not be loaded."
            print ("NEB works with an existing Matrix account. "
                "Please set up an account for NEB if you haven't already.'")
            print "The config for this account will be saved to '%s'" % args.config
            hsurl = raw_input("Home server URL (e.g. http://localhost:8008): ").strip()
            if hsurl.endswith("/"):
                hsurl = hsurl[:-1]
            username = raw_input("Full user ID (e.g. @user:domain): ").strip()
            password = raw_input("Password: ").strip()
            admin = raw_input("Admin full ID (who able to invite bot): ").strip()
            config = generate_config(hsurl, username, password, admin, args.config)
    else:
        a.print_help()
        print "You probably want to run 'python neb.py -c neb.config'"

    if config:
        main(config)
