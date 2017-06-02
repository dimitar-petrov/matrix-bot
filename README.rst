Bot
===

This is fork from generic client bot for Matrix which supports plugins.
It appeared because I'm sad to see that NEB is obsoleted by go-neb `Issue#21 <https://github.com/matrix-org/Matrix-NEB/issues/21>`_

This bot can:
-------------

- execute commands started from prefix ``!`` (this behavior is set by plugin design)
- react on every room message (this behavior is set by plugin design)
- react if user mention bot's name (this behavior is set by plugin design)
- call user by name when ansver (this behavior is set by plugin design)
- has commands with limited access by admins list (this behavior is set by plugin design)
- be extended by plugins (check `plug-in template <https://github.com/slipeer/matrix-bot/blob/master/matrix_bot/plugins/template.py>`_ to start plugin development)
- speak on users's language (if there is a corresponding localization. About preparing localization read in `LOCALE.rst <https://github.com/slipeer/matrix-bot/blob/master/LOCALE.rst>`_)
- be dynamical configured from chat room my limited bot administrators list
- can setup own avatar by provided url

Setup
=====

1. To install python package run:

    pip install https://github.com/slipeer/matrix-bot/tarball/master

2. To start bot run:

    matrix-bot -c <config location> [ -l <log location> ]

Bot configuration parameters described in `CONFIG.rst <https://github.com/slipeer/matrix-bot/blob/master/CONFIG.rst>`_

If the config file cannot be found, you will be asked to enter some settings for Bot and for loaded plugins (if nesesasry for plugin).

Create a room and invite Bot to it, and then type ``!help`` for a list of valid commands.

If need you can `start bot as Systemd service <https://github.com/slipeer/matrix-bot/blob/master/SYSTEMD.rst>`_

Register User for Bot
=====================

To register user for bot use command line script on server:

    register_new_matrix_user -u <username> -p <password> -a -c <path to homeserver.yaml with registration_shared_secret> <server URL>

or

    register_new_matrix_user -u <username> -p <password> -a -k <registration_shared_secret value from homeserver.yaml> <server URL>

or simple register new user in Riot and provide credentials to your bot.


Uninstall
=========

Installed python package can be removed by:

    pip uninstall matrix_bot



Plugins
=======

There *plugins* option in `config <https://github.com/slipeer/matrix-bot/blob/master/CONFIG.rst>`_:

- if it empty all plugins will be loaded
- if it contain plugins list - bot wil load only this plugins

Note! In plugin list you must use names as in plugin class in ``name`` property!

Bot stores plugins related data in working directory.

Template
--------

A `plug-in template <https://github.com/slipeer/matrix-bot/blob/master/matrix_bot/plugins/template.py>`_ 
starting point for the development of the plug-in. Demonstrates the main features of plugin API.
Start developing your own plug-in from it.

Config
------

- Allow online bot configuration management
- Allow view bot rooms
- Allow order bot to leave room (without the need for an administrator to join the room)
- Allow setup bot avatar

Google
------

- Provides ability to googling
- Provides ability to googling images
- Special command for show next search result

Wikipedia
---------

- Provides ability to search in wikipedia
- Result returned on same language as query (language must preset in locales)
- Result size limited, but at end provided link to page

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


