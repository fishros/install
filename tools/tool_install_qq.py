# -*- coding: utf-8 -*-
import glob
import os
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion, osarch
from .base import run_tool_file

# QQ 官网的下载地址是带 sign 和时间戳的临时链接, 只有从官网页面点下载时才会生成, 过期就 403,
# 脚本里写死的地址(原来的 linuxqq_3.2.1)早已失效. 所以改成: 用户在官网下载 deb, 脚本负责找到并安装
qq_download_page = "https://im.qq.com/linuxqq/index.shtml"
qq_deb_patterns = ["QQ_*.deb", "linuxqq_*.deb"]
download_dirs = ["下载", "Downloads"]


class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_INSTALL
        self.name = "一键安装QQ"
        self.author = '五柳小生'

    def find_qq_deb(self):
        """在各用户的 ~/下载 和 ~/Downloads 里找 QQ 安装包, 返回最新且架构匹配的一个"""
        debs = []
        for home in FileUtils.getusershome():
            for folder in download_dirs:
                for pattern in qq_deb_patterns:
                    debs += glob.glob(os.path.join(home, folder, pattern))
        debs.sort(key=os.path.getmtime, reverse=True)
        for deb in debs:
            result = CmdTask('dpkg-deb -f "{}" Architecture'.format(deb)).run()
            if result[0] != 0 or len(result[1]) == 0:
                PrintUtils.print_warn("{} 不是完整的安装包(可能没下载完), 跳过".format(deb))
                continue
            arch = result[1][0].strip()
            # 龙芯的包写 loongarch64, dpkg 报的是 loong64
            if arch.replace("loongarch64", "loong64") != osarch:
                PrintUtils.print_warn("{} 是{}版本, 和当前系统({})不符, 跳过".format(deb, arch, osarch))
                continue
            return deb
        return None

    def install_qq(self):
        deb = self.find_qq_deb()
        if deb is None:
            PrintUtils.print_warn("没有在「下载」目录里找到QQ安装包")
            PrintUtils.print_info("请先打开 {} 下载 deb 版(当前系统架构: {}), 下完再运行一次".format(qq_download_page, osarch))
            return False
        pkg = CmdTask('dpkg-deb -f "{}" Package'.format(deb)).run()[1][0].strip()
        PrintUtils.print_info("找到QQ安装包: {}, 开始安装~".format(deb))
        # 用 apt 装本地包, 缺的依赖会一起装上
        CmdTask('sudo DEBIAN_FRONTEND=noninteractive apt install -y "{}"'.format(deb), os_command=True).run()
        if "install ok installed" not in " ".join(CmdTask("dpkg-query -W -f='${Status}' " + pkg).run()[1]):
            PrintUtils.print_error("QQ安装失败, 请把上面的报错信息发到鱼香社区求助: https://fishros.org.cn/forum")
            return False
        PrintUtils.print_success("QQ安装成功~")
        return True

    def run(self):
        #正式的运行
        return self.install_qq()
