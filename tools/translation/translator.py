# -*- coding: utf-8 -*-
'''
A helper for translating string, inspired by Qt Linguist.
Author: Elysia
'''
import locale
import json
import os

COUNTRY_CODE_MAPPING = {
    "CN": "zh_CN",
    "US": "en_US"
}

class Linguist:

    _currentLocale = None

    def __init__(self):
        # Initialize the current locale.
        self._currentLocale = self.getLocalFromIP()
        if self._currentLocale is None:
            self._currentLocale = locale.getdefaultlocale()[0]
        
        # Load the translation file.
        self.loadTranslationFlile()

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
            os.system("""wget --header="Accept: application/json" --no-check-certificate "https://ip.renfei.net/" -O /tmp/fishros_check_country.json""")
            
            with open('/tmp/fishros_check_country.json', 'r') as json_file:  
                data = json.loads(json_file.read())

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
    