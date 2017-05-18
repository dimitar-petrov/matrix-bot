Start from systemd as service
=============================

 1. Install python package as described in README.md

 2. Create file:

 - /etc/default/matrix-bot - for service environment

 3. Create folders:

 - /etc/matrix-bot - for config
 - /var/lib/matrix-bot - for store plugin related data
 - /var/run/matrix-bot - for pid file store

 4. Run interactive command top generate config files:

    /usr/local/bin/matrix-bot -c /etc/matrix-bot/matrix-bot.json -l /var/log/matrix-bot.log -p /var/run/matrix-bot/matrix-bot.pid

or simple place ready config files for plugins to ``/var/lib/matrix-bot`` and main config to ``/etc/matrix-bot/matrix-bot.json``

 5. Make user for service runing:

    useradd -d /var/lib/matrix-bot matrix-bot

 6. Take ownership of all created folders to new user:

    chown  matrix-bot /etc/default/matrix-bot
    chown -R matrix-bot /var/lib/matrix-bot
    chown -R matrix-bot /var/run/matrix-bot
    chown -R matrix-bot /etc/matrix-bot
    chown matrix-bot /var/log/matrix-bot.log

 7. If you need locale template autogeneration, then give matrix-bot user write access to locale folder:

    chown -R matrix-bot <matrix-bot installation dir>/locale

 8. Copy systemd unit from contrib/systemd and use it:

    systemctl daemon-reload
    systemctl enable matrix-bot
    systemctl start matrix-bot

