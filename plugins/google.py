#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Slipeer@gmail.com'
from neb.plugins import Plugin
from neb.engine import KeyValueStore

import requests
import logging
log = logging.getLogger(name=__name__)


class GooglePlugin(Plugin):
    """Google search.
    (Default) google search <text to search>
    google image <text to search>
    """

    name = "google"
    default_method = "cmd_search"

    def __init__(self, *args, **kwargs):
        super(GooglePlugin, self).__init__(*args, **kwargs)
        self.store = KeyValueStore("google.json")

        if not self.store.has("apiurl"):
            self.store.set("apiurl", "https://www.googleapis.com/customsearch/v1")

        if not self.store.has("apikey"):
            print "API key is required to search with google customserchapi."
            apikey = raw_input("Google Custom Search API key: ").strip()
            if apikey:
                self.store.set("apikey", apikey)

        if not self.store.has("cx"):
            print "Custom search engine ID required to search with google customserchapi."
            cx = raw_input("Google Custom Search id (https://cse.google.com): ").strip()
            if cx:
                self.store.set("cx", cx)

    def cmd_search(self, event, *args):
        """Google search (default method). 'google search <text>'"""
        query = {}
        query["q"] = " ".join(args)
        query["num"] = 1
        query["start"] = 1
        query["imgSize"] = "large"
        query["alt"] = "json"
        query["key"] = self.store.get("apikey")
        query["cx"] = self.store.get("cx")
        r = requests.get(self.store.get("apiurl"), params=query)
        if "error" in r.json():
            log.error("Google search error: %r" % r.json()["error"])
        if "items" in r.json():
            return r.json()["items"][0]["link"]
        else:
            return "Nothing found..."

    def cmd_image(self, event, *args):
        """Google search image. 'google image <text>'"""
        query = {}
        query["q"] = " ".join(args)
        query["num"] = 1
        query["start"] = 1
        query["searchType"] = "image"
        query["imgSize"] = "large"
        query["alt"] = "json"
        query["key"] = self.store.get("apikey")
        query["cx"] = self.store.get("cx")
        r = requests.get(self.store.get("apiurl"), params=query)
        if "error" in r.json():
            log.error("Google search error: %r" % r.json()["error"])

        log.debug("Google query result: %r" % r.json())

        if "items" in r.json():
            i = requests.get(r.json()["items"][0]["link"])
            ires = self.matrix.media_upload(i.content, r.json()["items"][0]["mime"])
            if "content_uri" in ires:
                result = self.matrix.send_content(event["room_id"], ires["content_uri"], r.json()["items"][0]["title"], "m.image")
                return None
            else:
                log.error("Image upload error: %r" % ires)
                return "Image upload error"
        else:
            return "Nothing found..."

