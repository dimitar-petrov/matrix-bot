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
import gettext
import os
import langdetect
import logging as log


class locale(object):
    """ Translator tool class """

    def __init__(self, config, name='mistake'):
        self.config = config
        self.lang = 'en'
        # "matrix_bot.plugins."+self.name
        self.name = name
        self.lang_factory = langdetect.DetectorFactory()
        self.translations_root = os.path.join(self.config.rootf, "locale")
        # available translations
        self.langs = [
            name for name in os.listdir(
                self.translations_root
            ) if os.path.isdir(os.path.join(self.translations_root, name))
        ]
        self.lang_factory.load_profile(self._copy_lang([u'ru', u'en']))

    def _copy_lang(self, langs):
        """ Copy only nesesary language profiles.
        Returns new path."""
        import shutil
        for lang in langs:
            dstdir = os.path.join(os.getcwd(), 'lang_prof', self.name)
            try:
                os.makedirs(dstdir)
                # os.makedirs(self.name)
            except OSError as ose:
                # if not elready exists
                if not ose[0] == 17:
                    log.exception("Create dir for landuage profiles %r" % ose)
                pass
            except Exception as e:
                log.exception("Create dir for landuage profiles %r" % e)
                pass
            srcfile = os.path.join(langdetect.PROFILES_DIRECTORY, lang)
            try:
                shutil.copy(srcfile, dstdir)
            except Exception as e:
                log.exception("Copy landuage %s profile %r" % (lang, e))
                pass
        return dstdir

    def _detect(self, text):
        detector = self.lang_factory.create()
        detector.append(text)
        return detector.detect()

    def detect_lang(self, string):
        """ Detect string lang """
        self.lang = self._detect(string)
        log.debug("Detected lang: %s for string: %s." % (self.lang, string))

    def _find_key(self, input_dict, value):
        """ Returns key name from dict by value """
        return next((k for k, v in input_dict.items() if v == value), None)

    def untrans(self, cmd, module=None):
        """Backward translate cmd from detected language for module."""
        if not module:
            module = self.name
        uncmd = None
        self.detect_lang(cmd)
        try:
            trans = gettext.translation(
                module,
                self.translations_root,
                languages=[self.lang, 'en']
            )
            trans.install()
            uncmd = self._find_key(trans._catalog, trans.ugettext(cmd))
        except IOError as e:
            log.warn(
                "Translation for module %s non present in %s."
                % (module, self.translations_root)
            )
        except Exception as e:
            log.error(
                "UnTranslation: |%s|. For module: %s Exception: %r" % (cmd, module, e)
            )
            pass
        if not uncmd:
            uncmd = cmd
            self.lang = 'en'
        log.debug(
            "UnTranslation %s to: %s (DETECTED lang: %s)." % (cmd, uncmd, self.lang)
        )
        return uncmd

    def trans(self, string, module=None):
        """Translate string to language for module."""
        if not module:
            module = self.name
        # try translate string
        log.debug(
            "Translation: |%s|. To lang: %s for module %s" % (string, self.lang, module)
        )
        res = string
        try:
            trans = gettext.translation(
                module,
                self.translations_root,
                languages=[self.lang, 'en']
            )
            trans.install()
            res = trans.ugettext(string)
        except IOError as e:
            log.warn(
                "Translation for module %s non present in %s."
                % (module, self.translations_root)
            )
        except Exception as e:
            log.error(
                "Translation: %s. For module: %s Exception: %r" % (string, module, e)
            )
            pass
        log.debug("Translation %s to: %s (lang: %s)." % (string, res, self.lang))
        return res
