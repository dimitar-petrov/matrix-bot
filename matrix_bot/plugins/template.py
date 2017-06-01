# -*- coding: utf-8 -*-
# TODO Please save yor name for history
# Copyright <Year> <Author>
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
# TODO you can use KeyValueStore or RoomContextStore clases
# to store plugin data
from matrix_bot.mbot.store import KeyValueStore, RoomContextStore

# TODO Please save yor name for history
__author__ = 'Author <Author@email>'
log = logging.getLogger(name=__name__)

# TODO Create language files for plugin
# for tranclating docs look LOCALE.rst


# TODO Rename plugin
class TemplatePlugin(Plugin):
    # TODO describe your plugin
    """ New plugin template.
        Usage:
        'template first <text>'
        'template second <text>'
        'template third <text>'
        'template <text>'
        or if you write anything this plugin will receive it.
    """

    # TODO plugin name for config and commands
    name = 'template'

    # TODO You can hide plugin from main help
    hidden = False

    # TODO specify default method name
    # it will be called if no method specified
    default_method = 'cmd_default'

    # TODO create plugin constructor
    def __init__(self, *args, **kwargs):
        super(TemplatePlugin, self).__init__(*args, **kwargs)
        self.someopt = ''

    def cmd_default(self, event, *args):
        # TODO this strings will shown as help for users
        # it can (i think must) be translated
        """Template default method (default method). 'template default <text>'"""
        # TODO Do something with args array
        # It contains splited by space line after method name

        # TODO you can translate some text to users language
        # Is determined by the language on which the name of the method is typed
        # or you can pervously redetect user language by
        # self.tr.detect_lang("any user provided string")
        # detected language stored in self.tr.lang
        translated = self.tr.trans("some text")
        # TODO you can write to log
        log.info("Translated text %s" % translated)

        # TODO you can revert translation
        # This action redetects users language
        # and update self.tr.lang
        source_string = self.tr.untrans(translated)
        # TODO you can write to log
        log.info("Revert translation result %s" % source_string)

        # TODO return something
        # returned value will be posted as notice
        return None

    # TODO use @admin_only decorator for methods accessible only to bot admins
    @admin_only
    def cmd_second(self, event, *args):
        # TODO this strings will shown as help for users
        # it can (i think must) be translated
        """Template second method. 'template second <text>'"""
        # TODO Create translations for method names
        # and users can call it on own languages

        # TODO return something
        # you can return any type of message using
        # self.matrix.send_message or other methods
        return None

    # TODO use @civility if you need mention event sender in returned reply
    @civility
    def cmd_third(self, event, *args):
        # TODO this strings will shown as help for users
        # it can (i think must) be translated
        """Template third method. 'template third <text>'"""
        # TODO or you can retrive display name by this method
        your_name = self.get_displayname(event)

        # TODO return something
        # you can return any type of message using
        # self.matrix.send_message or other methods
        return "your name is %s" % your_name

    # TODO implement method executable for every message
    def on_msg(self, event, body):
        """Args:
            event: full message event
            body:  unformated message body
           Returns:
            returned value will be posted as notice
            if you need other message type then
            create it from matrix API call
            self.matrix.send_message"""

        # TODO you can check if message consist resort to bot
        if self.is_mentioned(body):
            # TODO you can write to log
            log.info("I was approached %s" % self.is_mentioned(body))
        pass
