Bot
===

This is fork from generic client bot for Matrix which supports plugins.
It appeared because I'm sad to see that NEB is obsoleted by go-neb `Issue#21 <https://github.com/matrix-org/Matrix-NEB/issues/21>`_

Setup
=====

1. To install python package run:

    pip install https://github.com/slipeer/Matrix-NEB/tarball/master

2. To start bot run:

    matrix-bot -c <config location> [ -l <log location> ]

If the config file cannot be found, you will be asked to enter some settings for Bot and for loaded plugins (if nesesasry fo plugin).

Invite bot to room can only users, specified in *admins* list in Bot config

Create a room and invite Bt to it, and then type ``!help`` for a list of valid commands.

Register User for Bot
=====================

To register user for bot use script:

    register_new_matrix_user -u <username> -p <password> -a -c <path to homeserver.yaml with registration_shared_secret> <server URL>

or

    register_new_matrix_user -u <username> -p <password> -a -k <registration_shared_secret value from homeserver.yaml> <server URL>


Uninstall
=========

Installed python package can be removed by:

    pip uninstall matrix_bot



Plugins
=======

There *plugins* option in config:

 - if it empty all plugins will be loaded
 - if it contain plugins list - bot wil load only this plugins

Note! In plugin list you must use names as in plugin class in ``name`` property!

Bot stores plugins related data in working directory.

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
