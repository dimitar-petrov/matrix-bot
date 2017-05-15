#!/usr/bin/env python
import argparse

from matrix_client.api import MatrixHttpApi
from matrix_client.errors import MatrixRequestError
from matrix_bot.mbot.engine import Engine
from matrix_bot.mbot.matrix import MatrixConfig

import inspect
import logging
import logging.handlers
import time
import os
import sys

log = logging.getLogger(name=__name__)

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
    except IOError as e:
        log.error("IOError with config file: %r" % e )
        pass
    except ValueError as e:
        log.error("ValueError with config file: %r" % e )
    except:
        log.error("Unexpected Error with config file: %r" % sys.exc_info()[0] )
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


def startup(config):
    # setup api/endpoint
    if not config.token:
        matrix = MatrixHttpApi(config.base_url)
        login = config.user_id[1:].split(":")[0]
        try:
            res = matrix.login(login_type="m.login.password", user=login, password=config.password)
        except MatrixRequestError as err:
            log.error("Login error: %r" % err)
            exit()
        log.debug("Login result: %r" % res)
        config.token = res["access_token"]
        config.save()
        matrix.token = config.token
    else:
        matrix = MatrixHttpApi(config.base_url, config.token)

    # setup engine
    engine = Engine(matrix, config)

    # Dytnamic plugin load from plugins folder
    lst = os.listdir("plugins")
    for fil in lst:
        name, ext = os.path.splitext(fil)
        if not os.path.isdir(os.path.join("plugins", fil)) and not fil[0] == "_" and ext in (".py"):
            try:
                mod = __import__("plugins." + name, fromlist = ["*"])
                for cls in  inspect.getmembers(mod, inspect.isclass):
                    if hasattr(cls[1], "name"):
                        if not config.plugins or cls[1].name in config.plugins:
                            engine.add_plugin(cls[1])
                            log.info("Load plugin %s (%s) from %s" % (
                                cls[1].name, cls[0], os.path.join("plugins", fil)
                            ))
                        else:
                            log.info("Skip plugin %s (%s) from %s - not listed in config" % (
                                cls[1].name, cls[0], os.path.join("plugins", fil)
                            ))
            except ImportError as err:
                log.error("Plugin module %s import error: %r" % (
                    "plugins." + fil, err
                ))

    engine.setup()

    while True:
        try:
            log.info("Listening for incoming events.")
            engine.event_loop()
        except Exception as e:
            log.error("Ruh roh: %s", e)
        time.sleep(5)

    log.info("Terminating.")

def main():
    a = argparse.ArgumentParser("Runs Matrix-bot. See plugins for commands.")
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
    log.info("  ===== Matrix-bot initialising ===== ")
    log.debug("Started as user: %s" % os.getlogin())
    config = None
    if args.config:
        log.info("Loading config from %s", args.config)
        config = load_config(args.config)
        log.info("Config %r", config)
        if not config:
            log.info("Setting up for an existing account.")
            print "Config file could not be loaded."
            print ("Matrix-bot works with an existing Matrix account. "
                "Please set up an account for Matrix-bot if you haven't already.'")
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
    print "You probably want to run 'python %s -c bot-config.json'" % os.path.basename(__file__)
    if config:
        startup(config)


if __name__ == '__main__':
    main()