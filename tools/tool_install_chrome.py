# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils, CmdTask, DownloadUtils
from .base import osarch

# Google 官方 deb, 国内直连实测约 8MB/s(2026-11). 装上后会自动加 Google 的 apt 源, 之后 apt upgrade 就能升级
CHROME_URL = "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
CHROME_PKG = "google-chrome-stable"


class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_INSTALL
        self.name = "一键安装Chrome浏览器"
        self.author = '小鱼'

    @staticmethod
    def installed_version():
        result = CmdTask("dpkg-query -W -f='${Status} ${Version}' " + CHROME_PKG).run()
        status = " ".join(result[1])
        if result[0] == 0 and "install ok installed" in status:
            return status.replace("install ok installed", "").strip()
        return None

    def install_chrome(self):
        # Ubuntu 22.04 自带的 snap 版 Firefox 在国内连不上 snap 商店、没法更新, 太老的版本打不开一些新网页(如 dsh web)
        if osarch != "amd64":
            PrintUtils.print_error("Google 只提供 amd64 版的 Linux Chrome, 当前系统架构是 {}, 请使用系统自带的浏览器".format(osarch))
            return False
        version = self.installed_version()
        if version:
            PrintUtils.print_success("已经安装了 Chrome {}, 以后用 sudo apt update && sudo apt upgrade 即可升级".format(version))
            return True
        PrintUtils.print_info("开始下载 Chrome 浏览器(约140MB)~")
        temp_file = "/tmp/fishros_chrome.deb"
        if not DownloadUtils.download_deb([("Google 官方", CHROME_URL)], temp_file):
            CmdTask('rm -f "{}"'.format(temp_file)).run()
            PrintUtils.print_error("Chrome 下载失败, 请检查网络后重试")
            return False
        # 用 apt 装本地包, 缺的依赖会一起装上
        CmdTask('sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "{}"'.format(temp_file), 600, os_command=True).run()
        CmdTask('rm -f "{}"'.format(temp_file)).run()
        version = self.installed_version()
        if not version:
            PrintUtils.print_error("Chrome 安装失败, 请把上面的报错信息发到鱼香社区求助: https://fishros.org.cn/forum")
            return False
        PrintUtils.print_success("Chrome {} 安装完成".format(version))
        PrintUtils.print_info("启动: 在应用菜单中搜索 Chrome, 或终端运行 google-chrome")
        PrintUtils.print_info("推荐设为默认浏览器: 首次打开 Chrome 时按提示设置, 或在 设置 -> 默认应用 -> 网页 里选 Google Chrome")
        return True

    def run(self):
        return self.install_chrome()
