Localization Naming
===================

All locale files must be placed to ``locale\<lang>\LC_MESSAGES\<module name>.pot``
 and then converted to locale\<lang>\LC_MESSAGES\<module name>.mo by runing:

    msgfmt ./<module name>.pot  --output-file ./<module name>.mo

or for all files:

    find -name '*.pot' -print | sed -e "p;s/^\(.*\).pot$/--output-file \1.mo/" | xargs -n3 msgfmt