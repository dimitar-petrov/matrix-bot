Bot
===

This is fork from generic client bot for Matrix which supports plugins.
It appeared because I'm sad to see that NEB is obsoleted by go-neb `Issue#21 <https://github.com/matrix-org/Matrix-NEB/issues/21>`_

Setup
=====

Run:

    ``python neb.py -c <config location> [ -l <log location> ]``

If the config file cannot be found, you will be asked to enter some settings for Bot and for loaded plugins (if nesesasry fo plugin).

Invite bot to room can only users, specified in *admins* list in Bot config

Create a room and invite Bt to it, and then type ``!help`` for a list of valid commands.



Plugins
=======

There *plugins* option in config:

 - if it empty all plugins will be loaded
 - if it contain plugins list - bot wil load only this plugins

Google
------

 - Provides ability to googling 
 - Provides ability to googling images

Github
------

 - Processes webhook requests and send messages to interested rooms.
 - Supports secret token HMAC authentication.
 - Supported events: ``push``, ``create``, ``ping``, ``pull_request``

Jenkins
-------

 - Sends build failure messages to interested rooms.
 - Support via the Notification plugin.
 - Supports shared secret authentication.

JIRA
----

 - Processes webhook requests and sends messages to interested rooms.
 - Resolves JIRA issue IDs into one-line summaries as they are mentioned by other people.


Guess Number
------------

 - Basic guess-the-number game.

URL
---

 - Provides URL encoding/decoding.

B64
---
 - Provides base64 encoding/decoding.
