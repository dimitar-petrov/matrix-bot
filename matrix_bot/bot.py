#!/usr/bin/env python
import argparse

from matrix_client.api import MatrixHttpApi
from matrix_client.errors import MatrixRequestError
from matrix_bot.mbot.engine import Engine
from matrix_bot.mbot.matrix import MatrixConfig
import matrix_bot

import inspect
import logging
import logging.handlers
import time
import os
import json
import sys
# For ssl verify silence
import warnings

log = logging.getLogger(name=__name__)


def generate_config(url, username, password, admin, config_loc):
    config = MatrixConfig({
        'url': url,
        'user_id': username,
        'password': password,
        'admins': admin,
        'case_insensitive': False
    }, config_loc)
    config.save()
    return config


def load_config(loc):
    #    try:
    with open(loc, 'r') as f:
        return MatrixConfig.from_file(f)
    #    except IOError as e:
    #        log.error("IOError with config file: %r" % e)
    #        pass
    #    except ValueError as e:
    #        log.error("ValueError with config file: %r" % e)
    #    except KeyError as e:
    #        log.error("KeyError with config file: %r" % e)
    #    except:
    #        log.error("Unexpected Error with config file: %r" % sys.exc_info())
    #        pass


def configure_logging(logfile):
    # Not need timestamp for stdin - systemd adds it
    log_format = "%(levelname)s: %(message)s"
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format
    )
    # Do not print requests DEBUG output
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.ERROR)
    # Once warn if we do not verify server ssl cert
    warnings.simplefilter("once")

    if logfile:
        log_file_format = "%(asctime)s %(levelname)s: %(message)s"
        formatter = logging.Formatter(log_file_format)

        # rotate logs (20MB, max 6 = 120MB)
        handler = logging.handlers.RotatingFileHandler(
              logfile, maxBytes=(1000 * 1000 * 20), backupCount=5)
        handler.setFormatter(formatter)
        logging.getLogger('').addHandler(handler)


def startup(config):
    # setup api/endpoint
    login = config.json['user_id'][1:].split(":")[0]
    if not config.json['token']:
        matrix = MatrixHttpApi(config.json['url'])
        matrix.validate_certificate(config.json['cert_verify'])
        try:
            res = matrix.login(
                login_type="m.login.password",
                user=login,
                password=config.json['password']
            )
        except MatrixRequestError as err:
            log.error("Login error: %r" % err)
            exit()
        log.debug("Login result: %r" % res)
        config.json['token'] = res["access_token"]
        matrix.token = config.json['token']
    else:
        matrix = MatrixHttpApi(config.json['url'], config.json['token'])
        matrix.validate_certificate(config.json['cert_verify'])

    config.save()

    # Update Display Name if needed
    cur_dn = matrix.get_display_name(config.json['user_id'])
    if not login == cur_dn:
        matrix.set_display_name(config.json['user_id'], login)

    # root path for plugin search and locale load
    config.rootf = os.path.dirname(os.path.abspath(matrix_bot.__file__))
    log.debug("Matrix_bot root folder: %s" % config.rootf)
    log.debug("Matrix_bot configuration: %s" % json.dumps(
        config.json,
        indent=4,
        sort_keys=True
    ))

    # setup engine
    engine = Engine(matrix, config)
    # Dytnamic plugin load from plugins folder
    osppath = os.path.join(config.rootf, "plugins")
    lst = os.listdir(osppath)
    for fil in lst:
        name, ext = os.path.splitext(fil)
        if (
            not os.path.isdir(os.path.join(osppath, fil)) and
            not fil[0] == "_" and ext in (".py")
        ):
            try:
                mod = __import__("matrix_bot.plugins."+name, fromlist=["*"])
                for cls in inspect.getmembers(mod, inspect.isclass):
                    if hasattr(cls[1], "name"):
                        if not config.json['plugins'] or cls[1].name in config.json['plugins']:
                            engine.add_plugin(cls[1])
                            log.info("Load plugin %s (%s) from %s" % (
                                cls[1].name, cls[0], os.path.join("plugins", fil)
                            ))
                        else:
                            log.info(
                                "Skip plugin %s (%s) from %s - not listed in config" % (
                                    cls[1].name, cls[0], os.path.join("plugins", fil)
                                )
                            )
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
    a.add_argument(
        "-p", "--pid-file", dest="pid",
        help="Save pid to this file."
    )
    args = a.parse_args()
    configure_logging(args.log)
    if args.pid:
        if os.path.isfile(args.pid):
            log.error("Pid file %s exists" % args.pid)
        try:
            file(args.pid, 'w').write(str(os.getpid()))
        except:
            log.error("Unexpected Error with pid file: %r" % sys.exc_info()[0])

    log.info("  ===== Matrix-bot initialising ===== ")
    config = None
    if args.config:
        log.info("Loading config from %s", args.config)
        config = load_config(args.config)
        log.info("Config %r", config)
        if not config:
            log.info("Setting up for an existing account.")
            print("Config file could not be loaded.")
            print(
                "Matrix-bot works with an existing Matrix account. "
                "Please set up an account for Matrix-bot if you haven't already.'"
            )
            print("The config for this account will be saved to '%s'" % args.config)
            hsurl = raw_input("Home server URL (e.g. http://localhost:8008): ").strip()
            if hsurl.endswith("/"):
                hsurl = hsurl[:-1]
            username = raw_input("Full user ID (e.g. @user:domain): ").strip()
            password = raw_input("Password: ").strip()
            admin = raw_input("Admin full ID (who able to invite bot): ").strip()
            config = generate_config(hsurl, username, password, admin, args.config)
    else:
        a.print_help()
        print(
            "Usage: 'python %s -c bot-config.json'" % os.path.basename(__file__)
        )
    if config.json:
        startup(config)


if __name__ == '__main__':
    main()
