# -*- coding: utf-8 -*-
'''
A helper for translating string, inspired by Qt Linguist.
Author: Elysia
'''
import locale
import json
import os
import tools.base
from tools.base import CmdTask

_suported_languages = ['zh_CN', 'en_US']
url_prefix = os.environ.get('FISHROS_URL','http://mirror.fishros.com/install')
lang_url = os.path.join(url_prefix,'tools/translation/assets/{}.py')

COUNTRY_CODE_MAPPING = {
    "CN": "zh_CN",
    "US": "en_US"
}

class Linguist:

    _currentLocale = None

    def __init__(self):
        # Initialize the current locale.
        self.country = 'CN'
        self._currentLocale = self.getLocalFromIP()
        if self._currentLocale is None:
            self._currentLocale = locale.getdefaultlocale()[0]
        # Load the translation file.
        self.lang = self._currentLocale
        for lang in _suported_languages:
            CmdTask("wget {} -O /tmp/fishinstall/{} --no-check-certificate".format(lang_url.format(lang),lang_url.format(lang).replace(url_prefix,''))).run()
        
        self.loadTranslationFlile()
        tools.base.tr = self

    def loadTranslationFlile(self):
        # Load the translation file.
        import importlib
        try:
            _import_command = f"tools.translation.assets.{self._currentLocale}"
            self._translations = importlib.import_module(_import_command).translations
        except Exception:
            # If the translation file does not exist, use the default translation file.
            _import_command = f"tools.translation.assets.en_US"
            self._translations = importlib.import_module(_import_command).translations

    def tr(self, string) -> str:
        # Check whether the string exists in the translation file.
        if self._currentLocale is not None and string in self._translations:
            return self._translations[string]
        else:
            # If the string does not exist, return the original string.
            return string

    def getLocalFromIP(self) -> str:
        local_str = ""
        try:
            os.system("""wget --header="Accept: application/json" --no-check-certificate "https://ip.renfei.net/" -O /tmp/fishros_check_country.json -qq""")
            with open('/tmp/fishros_check_country.json', 'r') as json_file:  
                data = json.loads(json_file.read())
                self.ip_info = data
                self.country = data['location']['countryCode']
                if data['location']['countryCode'] in COUNTRY_CODE_MAPPING:
                    local_str = COUNTRY_CODE_MAPPING[data['location']['countryCode']]
                else:
                    local_str = "en_US"
        except Exception:
            local_str = "en_US"
        finally:
            os.system("rm -f /tmp/fishros_check_country.json")

        return local_str

if __name__ == "__main__":
    # Test funcs
    tr = Linguist()
    