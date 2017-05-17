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
from matrix_bot.mbot.plugins import Plugin
import logging
import sys
import re
import math

__author__ = 'Pavel Kardash <Slipeer@gmail.com>'
log = logging.getLogger(name=__name__)


class CalcPlugin(Plugin):
    """Try to Calculate expression.
    Enter a mathematical expression
    and complete it with a = sign.
    If the expression can be computed,
    you will see the result."""

    name = "calc"
    integers_re = re.compile(r'\b[\d\.]+\b')

    def on_msg(self, event, body):
        body = event["content"]["body"].strip()
        if body.endswith("="):
            answer = body

            def int_to_float(match):
                group = match.group()
                if group.find('.') == -1:
                    return group + '.0'
                return group

            body = body[:-1]
            body = body.replace('^', '**')
            body = self.integers_re.sub(int_to_float, body)
            try:
                res = eval(body, dict(__builtins__=None), vars(math))
                return "%s%s" % (answer, str(res))
            except:
                log.error(
                    "Unexpected Error with calculation: %r %r" % (
                        sys.exc_info()[0],
                        sys.exc_info()[1]
                    )
                )
                pass
