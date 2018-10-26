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

import json


class KeyValueStore(object):
    """A persistent JSON file store."""

    def __init__(self, store_name, version='1'):
        self.config = {
            'version': version
        }
        self.config_loc = store_name+'.json'
        self._load()

    def _load(self):
        try:
            with open(self.config_loc, 'r') as f:
                self.config = json.loads(f.read())
        except:
            self._save()

    def _save(self):
        with open(self.config_loc, 'w') as f:
            f.write(json.dumps(self.config, indent=4))

    def has(self, key):
        return key in self.config

    def set(self, key, value, save=True):
        self.config[key] = value
        if save:
            self._save()

    def get(self, key):
        return self.config[key]


class RoomContextStore(object):
    """Stores state events for rooms."""

    def __init__(self, event_types, content_only=True):
        """Init the store.

        Args:
            event_types(list<str>): The state event types to store.
            content_only(bool): True to only store the content for state events.
        """
        self.state = {}
        self.types = event_types
        self.content_only = content_only

    def get_content(self, room_id, event_type, key=""):
        if self.content_only:
            return self.state[room_id][(event_type, key)]
        else:
            return self.state[room_id][(event_type, key)]["content"]

    def get_room_ids(self):
        return self.state.keys()

    def update(self, event):
        try:
            room_id = event["room_id"]
            etype = event["type"]
            if etype in self.types:
                if room_id not in self.state:
                    self.state[room_id] = {}
                key = (etype, event["state_key"])

                s = event
                if self.content_only:
                    s = event["content"]

                self.state[room_id][key] = s
        except KeyError:
            pass

    def init_from_sync(self, sync):
        for room_id in sync["rooms"]["join"]:
            # see if we know anything about these rooms
            room = sync["rooms"]["join"][room_id]

            self.state[room_id] = {}

            try:
                for state in room["state"]["events"]:
                    if state["type"] in self.types:
                        key = (state["type"], state["state_key"])

                        s = state
                        if self.content_only:
                            s = state["content"]

                        self.state[room_id][key] = s
            except KeyError:
                pass
