# -*- coding: utf-8 -*-
# Notes:
# matrix_endpoint
#   listen_for(["event.type", "event.type"])
# web_hook_server
#   register_hook("name", cb_fn)
# matrix_api
#   send_event(foo, bar)
#   send_message(foo, bar)

from functools import wraps
import inspect
import json
from matrix_bot.mbot.tools import locale

import logging as log


def admin_only(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        config = args[0].config
        event = args[1]
        if event["sender"] not in config.admins:
            return "Sorry, only %s can do that." % json.dumps(config.admins)
        result = fn(*args, **kwargs)
        return result
    return wrapped


class CommandNotFoundError(Exception):
    pass


class PluginInterface(object):

    def __init__(self, matrix_api, config, web_hook_server):
        self.matrix = matrix_api
        self.config = config
        self.webhook = web_hook_server
        self.tr = locale(config, "matrix_bot.plugins."+self.name)

    def run(self, event, arg_str):
        """Run the requested command.

        Args:
            event(dict): The raw event
            arg_str(list<str>): The parsed arguments from the event
        Returns:
            str: The message to respond with.
            list<str>: The messages to respond with.
            dict : The m.room.message content to respond with.
        """
        pass

    def on_sync(self, response):
        """Received initial sync results.

        Args:
            response(dict): The raw initialSync response.
        """
        pass

    def on_event(self, event, event_type):
        """Received an event.

        Args:
            event(dict): The raw event
            event_type(str): The event type
        """
        pass

    def on_msg(self, event, body):
        """Received an m.room.message event."""
        pass

    def is_mentioned(self, body):
        """Return mentioned text if Bot mentioned by display name or False"""
        pass

    def get_webhook_key(self):
        """Return a string for a webhook path if a webhook is required."""
        pass

    def on_receive_webhook(self, data, ip, headers):
        """Someone hit your webhook.

        Args:
            data(str): The request body
            ip(str): The source IP address
            headers: A dict of headers (via .get("headername"))
        Returns:
            A tuple of (response_body, http_status_code, header_dict) or None
            to return a 200 OK. Raise an exception to return a 500.
        """
        pass


class Plugin(PluginInterface):

    def run(self, event, arg_str):

        def is_ascii(s):
            """ Check that string pure ascii """
            return all(ord(c) < 128 for c in s)

        args_array = [arg_str]
        try:
            args_array = arg_str.split()
        except ValueError:
            pass  # may be 1 arg without need for quotes

        self.tr.detect_lang(event["content"]["body"].strip())
        if len(args_array) == 0:
            raise CommandNotFoundError(self.tr.trans(self.__doc__))

        # Structure is cmd_foo_bar_baz for "!foo bar baz"
        # This starts by assuming a no-arg cmd then getting progressively
        # more general until no args remain (in which case there isn't a match)
        for index, arg in enumerate(args_array):
            possible_method = '_'.join(args_array[:(len(args_array) - index)])
            if self.config.case_insensitive:
                possible_method = possible_method.lower()
            possible_method = self.tr.untrans(possible_method)
            if not is_ascii(possible_method):
                continue
            possible_method = 'cmd_'+possible_method
            if hasattr(self, possible_method):
                method = getattr(self, possible_method)
                remaining_args = args_array[len(args_array) - index:]

                # function params prefixed with "opt_" should be None if they
                # are not specified. This makes cmd definitions a lot nicer for
                # plugins rather than a generic arg array or no optional extras
                fn_param_names = inspect.getargspec(method)[0][1:]  # remove self
                if len(fn_param_names) > len(remaining_args):
                    # pad out the ones at the END marked "opt_" with None
                    for i in reversed(fn_param_names):
                        if i.startswith('opt_'):
                            remaining_args.append(None)
                        else:
                            break

                try:
                    if remaining_args:
                        return method(event, *remaining_args)
                    else:
                        return method(event)
                except TypeError as e:
                    log.exception(e)
                    raise CommandNotFoundError(self.tr.trans(method.__doc__))

        # if defined default command
        if hasattr(self, "default_method"):
            method = getattr(self, self.default_method)
            remaining_args = [event] + args_array

            # function params prefixed with "opt_" should be None if they
            # are not specified. This makes cmd definitions a lot nicer for
            # plugins rather than a generic arg array or no optional extras
            fn_param_names = inspect.getargspec(method)[0][1:]  # remove self
            if len(fn_param_names) > len(remaining_args):
                # pad out the ones at the END marked "opt_" with None
                for i in reversed(fn_param_names):
                    if i.startswith("opt_"):
                        remaining_args.append(None)
                    else:
                        break
            try:
                if remaining_args:
                    return method(*remaining_args)
                else:
                    return method()
            except TypeError as e:
                log.exception(e)
                raise CommandNotFoundError(self.tr.trans(method.__doc__))

        raise CommandNotFoundError(self.tr.trans("Unknown command"))

    def is_mentioned(self, body):
        mention = body.find(self.config.login+":")+1
        if mention:
            return body[mention-1:]
        else:
            return False
