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
import subprocess
import time

_suported_languages = ['zh_CN', 'en_US']
url_prefix = os.environ.get('FISHROS_URL','')
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
        # Create directory for downloads
        CmdTask("mkdir -p /tmp/fishinstall/tools/translation/assets").run()
        if url_prefix:
            for lang in _suported_languages:
                # Add timeout and retry mechanism for downloading language files
                # Use /tmp/ directory directly to avoid permission issues
                temp_file = "/tmp/fishros_lang_{}.py".format(lang)
                final_path = "/tmp/fishinstall/{}".format(lang_url.format(lang).replace(url_prefix, ''))
                download_cmd = "wget {} -O {} --no-check-certificate --timeout=10 --tries=3".format(lang_url.format(lang), temp_file)
                result = CmdTask(download_cmd).run()
                # Move file to final destination if download was successful
                if result[0] == 0:
                    CmdTask("mkdir -p $(dirname {})".format(final_path)).run()
                    CmdTask("mv {} {}".format(temp_file, final_path)).run()
                else:
                    # Clean up temp file if download failed
                    CmdTask("rm -f {}".format(temp_file)).run()
            
        self.loadTranslationFile()
        tools.base.tr = self

    def loadTranslationFile(self):
        # Load the translation file.
        import importlib
        try:
            _import_command = "tools.translation.assets.{}".format(self._currentLocale)
            self._translations = importlib.import_module(_import_command).translations
        except Exception:
            # If the translation file does not exist, use the default translation file.
            _import_command = "tools.translation.assets.en_US"
            self._translations = importlib.import_module(_import_command).translations

    def tr(self, string) -> str:
        # Check whether the string exists in the translation file.
        if self._currentLocale is not None and string in self._translations:
            return self._translations[string]
        else:
            # If the string does not exist, return the original string.
            return string

    def isCN(self) -> bool:
        return self.country == 'CN'
    
    def getLocalFromIP(self) -> str:
        local_str = ""
        temp_file = "/tmp/fishros_check_country.json"
        try:
            # Add timeout for IP detection
            result = subprocess.run(["wget", "--header=Accept: application/json", "--no-check-certificate", 
                                   "https://ip.renfei.net/", "-O", temp_file, "-qq", "--timeout=10"], 
                                  capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                with open(temp_file, 'r') as json_file:  
                    data = json.loads(json_file.read())
                    self.ip_info = data
                    self.country = data['location']['countryCode']
                    if data['location']['countryCode'] in COUNTRY_CODE_MAPPING:
                        local_str = COUNTRY_CODE_MAPPING[data['location']['countryCode']]
                    else:
                        local_str = "en_US"
            else:
                local_str = "en_US"
        except Exception:
            local_str = "en_US"
        finally:
            try:
                os.remove(temp_file)
            except:
                pass

        return local_str

if __name__ == "__main__":
    # Test funcs
    tr = Linguist()
