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
import logging
import json
from matrix_bot.mbot.store import KeyValueStore, RoomContextStore

__author__ = 'Slipeer <slipeer@gmail.com>'
log = logging.getLogger(name=__name__)


class ConfigPlugin(Plugin):
    # TODO describe your plugin
    """ Administrate bot.
        Usage:
        'config list'
        'config save'
        'config set <param>=<val>'
    """

    name = 'config'
    hidden = True

    # TODO specify default method name
    # it will be called if no method specified
    default_method = 'cmd_list'

    # TODO create plugin constructor
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
                res.append("%s = <removed for secutiry>" % param)
            else:
                res.append("%s = %s" % (param, _to_str(self.config.json[param])))
        return res

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
        return ("Setup param: `%s` to value: %s type: %s" % (param, val, type(val)))


    @admin_only
    def cmd_save(self, event, *args):
        """Save current bot configuration. Usage: 'config save'"""
        self.config.save()
        return "Configuration saved."

