Localization Naming
===================

All locale files must be placed to ``locale\<lang>\LC_MESSAGES\<module name>.pot``
 and then converted to locale\<lang>\LC_MESSAGES\<module name>.mo by runing:

    msgfmt ./<module name>.pot  --output-file ./<module name>.mo

or for all files:

    find -name '*.pot' -print | sed -e "p;s/^\(.*\).pot$/--output-file \1.mo/" | xargs -n3 msgfmt

If bot can write access to locale dir, then it try autoappend unpresent msgid to locale pot file.

Plugin name translation must be included to matrix_bot.mbot.engine.pot (engine module will look for it).