# -*- coding: utf-8 -*-
'''
A helper for translating string, inspired by Qt Linguist.
Author: Elysia
'''
import locale

class Linguist:

    _currentLocale = None

    def __init__(self):
        # Initialize the current locale.
        self._currentLocale = locale.getdefaultlocale()[0]
        if self._currentLocale is None:
            self._currentLocale = 'en_US'
        
        # Load the translation file.
        self.loadTranslationFlile()

    def loadTranslationFlile(self):
        # Load the translation file.
        global_vars = {}
        try :
            _import_command = f"from assets.{self._currentLocale} import translations as _translations"
            exec(_import_command, global_vars)
        except Exception:
            # If the translation file does not exist, use the default translation file.
            _import_command = f"from assets.en_US import translations as _translations"
            exec(_import_command, global_vars)

        self._translations = global_vars['_translations']

    def tr(self, string):
        # Check whether the string exists in the translation file.
        if string in self._translations:
            return self._translations[string]
        else:
            # If the string does not exist, return the original string.
            return string
    