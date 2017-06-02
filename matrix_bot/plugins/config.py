# -*- coding: utf-8 -*-
# Copyright 2017 Slipeer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from matrix_bot.mbot.plugins import Plugin, admin_only, civility
import requests
import logging
import json
from matrix_bot.mbot.store import KeyValueStore, RoomContextStore

__author__ = 'Slipeer <slipeer@gmail.com>'
log = logging.getLogger(name=__name__)


class ConfigPlugin(Plugin):
    """ Administrate bot.
        Usage:
        'config list'
        'config save'
        'config rooms'
        'config leave <room_id>'
        'config set <param>=<val>'
        'config avatar <avatar image url>'
    """

    name = 'config'
    hidden = True

    default_method = 'cmd_list'

    def __init__(self, *args, **kwargs):
        super(ConfigPlugin, self).__init__(*args, **kwargs)
        self.someopt = ''

    def cmd_default(self, event, *args):
        """Template default method (default method). 'template default <text>'"""
        return None

    @admin_only
    def cmd_list(self, event, *args):
        """Show bot configuration. Usage: 'config list'"""

        def _to_str(val):
            if isinstance(val, bool):
                return str(val)
            if isinstance(val, int):
                return str(val)
            if isinstance(val, list):
                return '['+', '.join([_to_str(m) for m in val])+']'
            return "'"+str(val)+"'"

        res = ["Configuration:"]
        for param in self.config.json:
            if param in ('password', 'token'):
                res.append("%s = &lt;removed for secutiry&gt;" % param)
            else:
                res.append("%s = %s" % (param, _to_str(self.config.json[param])))
        self.send_html(event['room_id'], '<br>'.join(res))
        return None

    @admin_only
    def cmd_rooms(self, event, *args):
        """Show bot rooms. Usage: 'config rooms'"""
        rooms = []
        for room in self.config.rooms:
            room_name = self.matrix.get_room_name(room)
            rooms.append("%s (%s)" % (room, room_name.get('name')))
        self.send_html(event['room_id'], "['"+"', '".join(rooms)+"']")

    @admin_only
    def cmd_leave(self, event, *args):
        """Leave room. Usage: 'config leave <room_id>'"""
        if len(args) < 1:
            room_id = event['room_id']
        else:
            room_id = args[0]
        self.matrix.leave_room(room_id)

    @admin_only
    def cmd_set(self, event, *args):
        """Set bot configuration value. Usage: 'config set <param>=<val>'"""
        (param, val) = ' '.join(args).split("=")
        param = param.strip()
        val = val.strip()
        if val == 'True':
            val = True
        elif val == 'False':
            val = False
        else:
            val = eval(val, dict(__builtins__=None))
        if param in self.config.json:
            if not type(val) == type(self.config.json[param]):
                return "Type error. Must be %s but received %s" % (
                    type(self.config.json[param]), type(val)
                )
        self.config.set(param, val)
        self.send_html(
            event['room_id'], "Setup param: `%s` to value: `%s`" % (param, val)
        )
        if param in ['plugins']:
            # needs restart to aply
            self.config.save()
            raise SystemExit('Need restart to apply config changes.')

    @admin_only
    def cmd_avatar(self, event, *args):
        """Set bot avatar. Usage: 'config avatar <avatar image url>'"""
        try:
            i = requests.get(' '.join(args), timeout=30)
        except ConnectionError as err:
            log.error(
                'Avatar image %s download error: %r'
                % (' '.join(args), err)
            )
            return 'Avatar image %s download error: %r' % (' '.join(args), err)
        if not i.status_code == requests.codes.ok:
            return 'Avatar image %s download error: %d' % (' '.join(args), i.status_code)
        log.debug('Avatar mime: %s' % i.headers['content-type'].split(';')[0])
        ires = self.matrix.media_upload(
            i.content,
            i.headers['content-type'].split(';')[0]
        )
        if 'content_uri' in ires:
            log.debug('Avatar uploaded: %s' % ires['content_uri'])
            self.matrix.set_avatar_url(
                self.config.json['user_id'],
                ires['content_uri'],
            )
        else:
            log.error('Avatar upload error: %r' % ires)
            return 'Avatar upload error: %r' % ires

    @admin_only
    def cmd_save(self, event, *args):
        """Save current bot configuration. Usage: 'config save'"""
        self.config.save()
        self.send_html(event['room_id'], 'Configuration saved')

