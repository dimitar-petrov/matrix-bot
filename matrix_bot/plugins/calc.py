#!/usr/bin/python
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

__author__ = 'Pavel Kardash <Slipeer@gmail.com>'
from matrix_bot.mbot.plugins import Plugin

import requests
import logging
import sys
log = logging.getLogger(name=__name__)


class CalcPlugin(Plugin):
    """
        Try to Calculate expression.
        Enter a mathematical expression 
        and complete it with a = sign.
        If the expression can be computed,
        you will see the result.
    """

    name = "calc"

    def on_msg(self, event, body):
        room_id = event["room_id"]
        body = event["content"]["body"].strip()
        if body.endswith("="):
            body = body[:-1]
            try:
                res = eval(body, {}, {})
                return "%s=%s" % (body, str(res))
            except:
                log.error("Unexpected Error with calculation: %r %r" % (sys.exc_info()[0], sys.exc_info()[1]) )
                pass

