# -*- coding: utf-8 -*-
'''
A helper for translating string, inspired by Qt Linguist.
Author: Elysia
'''
import locale
import xml.etree.ElementTree as ET
import os
import tools.base
from tools.base import CmdTask
import subprocess
import threading
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
        # 查 IP 所在国家要走一趟外网(约 1s), 放到后台和下载语言文件同时进行
        ip_result = []
        ip_thread = threading.Thread(target=lambda: ip_result.append(self.getLocalFromIP()))
        ip_thread.daemon = True
        ip_thread.start()
        if url_prefix:
            # 两个语言文件用一条命令下完: 原来 mkdir/wget/mv 拆成 6 条 CmdTask, 刷屏且每条都有额外等待
            # 先下到 /tmp/ 再挪过去, 避免目标目录权限问题; 下载失败就删掉半截文件
            download_cmds = ["mkdir -p /tmp/fishinstall/tools/translation/assets"]
            for lang in _suported_languages:
                temp_file = "/tmp/fishros_lang_{}.py".format(lang)
                final_path = "/tmp/fishinstall/{}".format(lang_url.format(lang).replace(url_prefix, ''))
                download_cmds.append("(wget -q {} -O {} -T 15 -t 3 --no-check-certificate && mv {} {} || rm -f {})".format(
                    lang_url.format(lang), temp_file, temp_file, final_path, temp_file))
            CmdTask("; ".join(download_cmds)).run()
        ip_thread.join(16)
        self._currentLocale = ip_result[0] if ip_result else None
        if self._currentLocale is None:
            # 查不到 IP 所在国家(断网、DNS 故障、接口不可用)时按系统语言来, 而不是一律英文
            self._currentLocale = self.getLocalFromSystem()
        # Load the translation file.
        self.lang = self._currentLocale

        self.loadTranslationFile()
        
        tools.base.tr = self

    def loadTranslationFile(self):
        # Load the translation file.
        import importlib
        try:
            _import_command = "tools.translation.assets.{}".format(self._currentLocale)
            self._translations = importlib.import_module(_import_command).translations
        except Exception:
            self._translations = []
            # If the translation file does not exist, use the default translation file.
            # _import_command = "tools.translation.assets.en_US"
            # self._translations = importlib.import_module(_import_command).translations

    def tr(self, string) -> str:
        # Check whether the string exists in the translation file.
        if self._currentLocale is not None and string in self._translations:
            return self._translations[string]
        else:
            # If the string does not exist, return the original string.
            return string

    def isCN(self) -> bool:
        return self.country == 'CN'
    
    @staticmethod
    def getLocalFromSystem() -> str:
        """
        按系统语言选: 英文系统用英文, 其它情况(中文、C/POSIX 等没有语言偏好)用中文(工具本身的语言).
        直接读环境变量: locale.getdefaultlocale() 会把 C.UTF-8 规范化成 en_US, 不能用
        """
        system_locale = ""
        for name in ("LC_ALL", "LC_MESSAGES", "LANG"):
            if os.environ.get(name):
                system_locale = os.environ[name].lower()
                break
        if system_locale.startswith("en"):
            return "en_US"
        return "zh_CN"

    def getLocalFromIP(self) -> str:
        local_str = ""
        temp_file = "/tmp/fishros_check_country.xml"
        try:
            # Add timeout for IP detection
            result = subprocess.run(["wget", "--header=Accept: application/xml", "--no-check-certificate", 
                                   "https://ip.renfei.net/", "-O", temp_file, "-qq", "--timeout=10"], 
                                  capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                with open(temp_file, 'r') as xml_file:  
                    self.ip_info = xml_file.read()
                root = ET.fromstring(self.ip_info)
                self.country = root.find('location/countryCode').text
                if self.country in COUNTRY_CODE_MAPPING:
                    local_str = COUNTRY_CODE_MAPPING[self.country]
                else:
                    local_str = "en_US"
            else:
                local_str = None
        except Exception:
            local_str = None
        finally:
            try:
                os.remove(temp_file)
            except:
                pass

        return local_str

if __name__ == "__main__":
    # Test funcs
    tr = Linguist()
