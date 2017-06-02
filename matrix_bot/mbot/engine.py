# -*- coding: utf-8 -*-
from matrix_client.api import MatrixError, MatrixRequestError
from matrix_bot.mbot import NebError
from matrix_bot.mbot.plugins import CommandNotFoundError
from matrix_bot.mbot.webhook import NebHookServer

import json
import logging as log
import pprint
from matrix_bot.mbot.tools import locale
import time


class Engine(object):
    """Orchestrates plugins and the matrix API/endpoints."""
    # Command prefix symbol
    PREFIX = "!"
    # Sync timeout in seconds! for matrix API
    SYNC_TIMEOUT=60
    # Pause in sync cycle in seconds
    SYNC_CYCLE_WAIT=1

    def __init__(self, matrix_api, config):
        self.plugin_cls = {}
        self.plugins = {}
        self.config = config
        self.matrix = matrix_api
        self.sync_token = None  # set later by initial sync
        self.tr = locale(config, __name__)

    def setup(self):
        self.webhook = NebHookServer(
            self.config.json['hook_host'],
            self.config.json['hook_port']
        )
        self.webhook.daemon = True
        self.webhook.start()

        # init the plugins
        log.debug("Init plugins")
        for cls_name in self.plugin_cls:
            self.plugins[cls_name] = self.plugin_cls[cls_name](
                self.matrix,
                self.config,
                self.webhook
            )

        sync = self.matrix.sync(timeout_ms=Engine.SYNC_TIMEOUT, since=self.sync_token)
        self.parse_sync(sync, initial_sync=True)
        log.debug("Notifying plugins of initial sync results")
        for plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin.on_sync(sync)

            # see if this plugin needs a webhook
            if plugin.get_webhook_key():
                self.webhook.set_plugin(plugin.get_webhook_key(), plugin)

    def _help(self):
        plugins = [self.tr.trans(name) for name in self.plugins.keys() if not self.plugins[name].hidden]
        return (
            self.tr.trans(
                "Installed plugins: %s - Type '%shelp <plugin_name>' for more."
            ) % (', '.join(plugins), Engine.PREFIX)
        )

    def add_plugin(self, plugin):
        log.debug("add_plugin %s", plugin)
        self.plugin_cls[plugin.name] = plugin

    def parse_membership(self, event):
        log.info("Parsing membership: %s", event)
        if (event["state_key"] == self.config.json['user_id']
                and event["content"]["membership"] == "invite"):
            user_id = event["sender"]
            if self.config.json.get('any_can_invite'):
                self.matrix.join_room(event["room_id"])
            elif user_id in self.config.json['admins']:
                self.matrix.join_room(event["room_id"])
            else:
                log.info(
                    "Refusing invite, %s not in admin list. Event: %s",
                    user_id, event
                )
                self.matrix.leave_room(event["room_id"])

    def plugin_reply(self, room, responses):
        if type(responses) == list:
            for res in responses:
                if type(res) in [str, unicode]:
                    self.matrix.send_message(
                        room,
                        res,
                        msgtype="m.notice"
                    )
                else:
                    self.matrix.send_message_event(
                        room, "m.room.message", res
                    )
        elif type(responses) in [str, unicode]:
            self.matrix.send_message(
                room,
                responses,
                msgtype="m.notice"
                )
        else:
            self.matrix.send_message_event(
                room, "m.room.message", responses
            )

    def parse_msg(self, event):
        body = event["content"]["body"].strip()
        if (event["sender"] == self.config.json['user_id'] or
                event["content"]["msgtype"] == "m.notice"):
            return
        room = event["room_id"]  # room_id added by us
        if body.startswith(Engine.PREFIX):
            # command in line
            try:
                segments = body.split()
                cmd = segments[0][1:]
                if self.config.json['case_insensitive']:
                    cmd = cmd.lower()

                # try untranslate CMD
                self.tr.detect_lang(cmd)
                cmd = self.tr.untrans(cmd)

                if cmd == "help":
                    if len(segments) == 2:
                        opt1 = self.tr.untrans(segments[1])
                        if opt1 in self.plugins:
                            # return help on a plugin
                            self.matrix.send_message(
                                room,
                                self.tr.trans(
                                    self.plugins[opt1].__doc__,
                                    "matrix_bot.plugins."+self.plugins[opt1].name
                                ),
                                msgtype="m.text"
                            )
                    else:
                        # return generic help
                        self.matrix.send_message(room, self._help(), msgtype="m.text")
                elif cmd in self.plugins:
                    plugin = self.plugins[cmd]
                    responses = None
                    try:
                        responses = plugin.run(
                            event,
                            # unicode(" ".join(body.split()[1:]).encode("utf8"))
                            ' '.join(body.split()[1:])
                        )
                    except CommandNotFoundError as e:
                        log.exception(e)
                        self.matrix.send_message(
                            room,
                            str(e),
                            msgtype="m.notice"
                        )
                    except MatrixRequestError as ex:
                        log.exception(ex)
                        self.matrix.send_message(
                            room,
                            "Problem making request: (%s) %s" % (ex.code, ex.content),
                            msgtype="m.notice"
                        )
                    if responses:
                        log.debug("[Plugin-%s] Response => %r", cmd, responses)
                        self.plugin_reply(room, responses)

            except NebError as ne:
                log.exception(ne)
                self.matrix.send_message(room, ne.as_str(), msgtype="m.notice")
            except Exception as e:
                log.exception(e)
                self.matrix.send_message(
                    room,
                    "Fatal error when processing command.",
                    msgtype="m.notice"
                )
        else:
            # on_msg() process for loaded plugins
            try:
                for p in self.plugins:
                    responses = self.plugins[p].on_msg(event, body)
                    if responses:
                        log.debug("[Plugin-%s on_msg()] Response => %s", p, responses)
                        self.plugin_reply(room, responses)
            except Exception as e:
                log.exception(e)

    def event_proc(self, event):
        etype = event["type"]
        switch = {
            "m.room.member": self.parse_membership,
            "m.room.message": self.parse_msg
        }
        try:
            switch[etype](event)
        except KeyError:
            try:
                for p in self.plugins:
                    self.plugins[p].on_event(event, etype)
            except Exception as e:
                log.exception(e)
        except Exception as e:
            log.error("Couldn't process event: %s", e)

    def event_loop(self):
        while True:
            try:
                # Danger!!! requests timeout is in seconds:
                # http://docs.python-requests.org/en/master/user/quickstart/#timeouts
                j = self.matrix.sync(timeout_ms=Engine.SYNC_TIMEOUT, since=self.sync_token)
            except MatrixError as ex:
                log.exception("Matrix Error %r" % ex)
            except Exception as e:
                log.error("Error when matrix sync %r" % e)
            self.parse_sync(j)
            # Some wait
            time.sleep(Engine.SYNC_CYCLE_WAIT)

    def parse_sync(self, sync_result, initial_sync=False):

        for room_id, left_room in sync_result["rooms"]['leave'].items():
            if room_id in self.config.rooms:
                del self.config.rooms[room_id]

        self.sync_token = sync_result["next_batch"]  # for when we start syncing

        # check invited rooms
        rooms = sync_result["rooms"]["invite"]
        for room_id in rooms:
            events = rooms[room_id]["invite_state"]["events"]
            self.process_events(events, room_id)

        # return early if we're performing an initial sync
        # (ie: don't parse joined rooms, just drop the state)
        if initial_sync:
            return

        # check joined rooms
        rooms = sync_result["rooms"]["join"]
        for room_id in rooms:
            if not self.config.rooms.get(room_id):
                self.config.rooms[room_id]={}
            events = rooms[room_id]["timeline"]["events"]
            self.process_events(events, room_id)

    def process_events(self, events, room_id):
        for event in events:
            event["room_id"] = room_id
            self.event_proc(event)
