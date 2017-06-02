Main configuration file format description
==========================================

Main configuration file has json format and contains following parameters:

user_id
-------

**mandatory**

*Type:* string

*Value:* Matrtix userid for bot

*Example value:* ``"@user:matrix.org"``

password
--------

**сan be omitted if ``token`` specified**

*Type:* string

*Value:* Matrtix user password

*Example value:* ``"SomeBigSecretForLittleCompany"``

token
-----

**set by bot if you have set a ``password``**

*Type:* string

*Value:* Matrtix authentification token

*Example value:* ``"SomeBigTokenString"``

url
---

*Type:* string

*Value:* Matrtix homeserver url

*Default value:* ``"https://matrix.org"``

cert_verify
-----------

*Type:* bool

*Value:* Whether to check homeserver certificate

*Default value:* ``true``

admins
------

*Type:* list of strings

*Value:* List Matrix users ids of bot admins.
Only admins can use plugins methods with ``@admin_only`` decorator.
``Config`` plugin has this decorator on all methods.
If ``any_can_invite`` not ``true`` (or not set) only admins can invite bot to room.

*Example value:* ``["@admin1:matrix.org", "@admin2:matrix.org"]``

any_can_invite
--------------

*Type:* bool

*Value:* Whether who can invite bot to rooms. If ``false`` only admins can invite bot - other invites will be rejected.
If admins list empty this option auto switch to ``true``

*Default value:* ``false``

case_insensitive
----------------

*Type:* bool

*Value:* Specifies the sensitivity of bot commands to characters case

*Default value:* ``true``

hook_host
---------

*Type:* string

*Value:* WebHook server bind address (uses by some plugins like github)

*Default value:* ``"0.0.0.0"``

hook_port
---------

*Type:* int

*Value:* WebHook server bind port (uses by some plugins like github)

*Default value:* ``8500``
