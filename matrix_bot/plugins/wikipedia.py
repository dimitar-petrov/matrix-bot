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

from matrix_bot.mbot.plugins import Plugin, civility
from matrix_bot.mbot.store import KeyValueStore
import logging
import requests

__author__ = 'Slipeer <Slipeer@gmail.com>'
log = logging.getLogger(name=__name__)


class WikipediaPlugin(Plugin):
    """ Wikipedia search plugin.
        Usage:
        'wiki <text to search>'
        Example:
        'wiki russian desman'
    """
    name = 'wiki'

    default_method = 'cmd_search'

    def __init__(self, *args, **kwargs):
        super(WikipediaPlugin, self).__init__(*args, **kwargs)
        self.store = KeyValueStore(self.name)
        if not self.store.has('apiurl'):
            self.store.set(
                'apiurl', 'https://%s.wikipedia.org/w/api.php'
            )
        self.lang = 'en'

    def _qwiki(self, query):
        """ Query wikipedia API """
        r = requests.get(self.store.get('apiurl') % self.lang, params=query)
        if 'error' in r.json():
            log.error('Wikipedia search: %r' % r.json()['error'])
            # return self.tr.trans('When searching on Wikipedia, an error occurred.')
        else:
            if 'warnings' in r.json():
                log.warn('Wikipedia search: %r' % r.json()['warnings'])
            if 'query' in r.json():
                if 'normalized' in r.json()['query']:
                    query['titles'] = r.json()['query']['normalized'][0]['to']
                    log.debug("Wikipedia query to %s is normalized to %s" % (
                        r.json()['query']['normalized'][0]['from'],
                        r.json()['query']['normalized'][0]['to']
                    ))
                    return self._qwiki(query)
                if 'pages' in r.json()['query']:
                    return r.json()['query']['pages']
                else:
                    log.debug('Wikipedia result without pages: %r %r' % (query, r.json()))
                    # return self.tr.trans('Nothing found.')

    def _get_url(self, pageid):
        """ Get wiki URL by pageid """
        query = {}
        query['action'] = 'query'
        query['prop'] = 'info'
        query['format'] = 'json'
        query['inprop'] = 'url'
        query['pageids'] = pageid

        r = requests.get(self.store.get('apiurl') % self.lang, params=query)
        if 'error' in r.json():
            log.error('Wikipedia search: %r' % r.json()['error'])
        else:
            if 'warnings' in r.json():
                log.warn('Wikipedia search: %r' % r.json()['warnings'])
            if 'query' in r.json():
                if 'pages' in r.json()['query']:
                    for page in r.json()['query']['pages']:
                        if 'fullurl' in r.json()['query']['pages'][page]:
                            return r.json()['query']['pages'][page]['fullurl']
        return None

    @civility
    def cmd_search(self, event, *args):
        """Search in wikipedia. 'wiki <text to search>'"""
        self.lang = self.tr.detect_lang(' '.join(args))
        query = {}
        query['action'] = 'query'
        query['prop'] = 'extracts'
        query['format'] = 'json'
        query['redirects'] = 1
        query['titles'] = ' '.join(args)

        res = []
        pages = self._qwiki(query)
        for page in pages:
            if 'extract' in pages[page]:
                self.send_html(
                    event['room_id'],
                    pages[page]['extract']
                )
            link = self._get_url(page)
            if link:
                res.append(link)
            if 'missing' in pages[page]:
                log.debug('Wikipedia result missing page: %r' % pages[page])
                return self.tr.trans('Page %s is missing') % ' '.join(args)
        # After text return collected links
        return res
