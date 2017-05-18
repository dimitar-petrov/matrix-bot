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
from matrix_bot.mbot.store import KeyValueStore
import requests
import logging

__author__ = 'Pavel Kardash <Slipeer@gmail.com>'
log = logging.getLogger(name=__name__)


class GooglePlugin(Plugin):
    """Google search.
    (Default) google search <text to search>
    google image <text to search>
    google next"""

    name = 'google'
    default_method = 'cmd_search'

    def __init__(self, *args, **kwargs):
        super(GooglePlugin, self).__init__(*args, **kwargs)
        self.store = KeyValueStore(self.name)
        self.search_state = {}

        if not self.store.has('apiurl'):
            self.store.set(
                'apiurl', 'https://www.googleapis.com/customsearch/v1'
            )

        if not self.store.has('apikey'):
            print('API key is required to search with google customserchapi.')
            apikey = raw_input('Google Custom Search API key: ').strip()
            if apikey:
                self.store.set('apikey', apikey)

        if not self.store.has('cx'):
            print(
                'Custom search engine ID required'
                'to search with google customserchapi.'
            )
            cx = raw_input('Google Custom Search id (https://cse.google.com): ').strip()
            if cx:
                self.store.set('cx', cx)

    def cmd_search(self, event, *args):
        """Google search (default method). 'google search <text>'"""
        query = {}
        query['q'] = ' '.join(args)
        query['num'] = 1
        query['start'] = 1
        query['alt'] = 'json'
        query['key'] = self.store.get('apikey')
        query['cx'] = self.store.get('cx')
        res = self._gquery(query, event)
        if 'items' in res:
            self.matrix.send_message(
                event['room_id'],
                res['items'][0]['link']
            )
            return None
        else:
            return self.tr.trans('Nothing found...')

    def cmd_image(self, event, *args):
        """Google search image. 'google image <text>'"""
        query = {}
        query['q'] = ' '.join(args)
        query['num'] = 1
        query['start'] = 1
        query['searchType'] = 'image'
        query['imgSize'] = 'large'
        query['alt'] = 'json'
        query['key'] = self.store.get('apikey')
        query['cx'] = self.store.get('cx')
        res = self._gquery(query, event)

        if 'items' in res:
            if self._send_image(res, event):
                return None
            else:
                return self.tr.trans('Image upload error.')
        else:
            return self.tr.trans('Nothing found...')

    def cmd_next(self, event, *args):
        """Search next. 'google next'"""
        if event['room_id'] in self.search_state:
            query = self.search_state[event['room_id']]
            query['start'] = query['start']+1
            res = self._gquery(query, event)
            if 'items' in res:
                if 'searchType' in query:
                    if query['searchType'] == 'image':
                        # image query
                        if self._send_image(res, event):
                            return None
                        else:
                            return self.tr.trans('Image upload error.')
                    else:
                        log.error(
                            'Strange query %r in room %s'
                            % (query, event['room_id'])
                        )
                else:
                    # simple query
                    self.matrix.send_message(
                        event['room_id'],
                        res['items'][0]['link']
                    )
                    return None
            else:
                return self.tr.trans('Nothing found...')
        else:
            return self.tr.trans('No pervous search in this room.')

    cmd_more = cmd_next
    """Search next. 'google more'"""

    def _send_image(self, res, event):
        """Send image to room"""
        # TODO add more error handling
        try:
            i = requests.get(res['items'][0]['link'], timeout=30)
        except ConnectionError as err:
            log.error(
                'Image %s download error: %r'
                % (res['items'][0]['link'], err)
            )
            return False
        ires = self.matrix.media_upload(i.content, res['items'][0]['mime'])
        if 'content_uri' in ires:
            self.matrix.send_content(
                event['room_id'],
                ires['content_uri'],
                res['items'][0]['title'],
                'm.image'
            )
            return True
        else:
            log.error('Image upload error: %r' % ires)
            return False

    def _gquery(self, query, event):
        """Google query func."""
        self.search_state[event['room_id']] = query
        r = requests.get(self.store.get('apiurl'), params=query)
        if 'error' in r.json():
            log.error('Google search error: %r' % r.json()['error'])

        log.debug('Google query result: %r' % r.json())
        return r.json()
