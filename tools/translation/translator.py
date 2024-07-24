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
            self._currentLocale = "en_US"
        
        # Load the translation file.
        self.loadTranslationFlile()

    def loadTranslationFlile(self):
        # Load the translation file.
        import importlib
        try :
            _import_command = f"tools.translation.assets.{self._currentLocale}"
            self._translations = importlib.import_module(_import_command).translations
        except Exception:
            # If the translation file does not exist, use the default translation file.
            pass

    def tr(self, string) -> str:
        # Check whether the string exists in the translation file.
        if self._currentLocale is not None and string in self._translations:
            return self._translations[string]
        else:
            # If the string does not exist, return the original string.
            return string
    