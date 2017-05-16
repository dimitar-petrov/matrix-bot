from matrix_bot.mbot.plugins import Plugin

import urllib


class UrlPlugin(Plugin):
    """URL encode or decode text.
    url encode <text>
    url decode <text>
    """

    name = "url"

    def cmd_encode(self, event, *args):
        """URL encode text. 'url encode <text>'"""
        # use the body directly so quotes are parsed correctly.
        return urllib.quote(u' '.join(args).encode("utf8"))

    def cmd_decode(self, event, *args):
        """URL decode text. 'url decode <url encoded text>'"""
        # use the body directly so quotes are parsed correctly.
        return urllib.unquote(u' '.join(args).encode("utf8"))
