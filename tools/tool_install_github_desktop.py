# -*- coding: utf-8 -*-
import re
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file

# 原来走 github.fishros.org 中转下载写死的 2.9.12, 中转已不返回数据(wget 会卡几十分钟).
# 改用 shiftkey 项目 README 里给出的官方 apt 镜像, 国内实测约 1.7MB/s; 从它的软件包索引里取最新版下载,
# 不把它加成 apt 源: 镜像万一挂了, apt update 会一直报错, 连累其它工具
mwt_mirror = "https://mirror.mwt.me/shiftkey-desktop/deb"
github_releases = "https://github.com/shiftkey/desktop/releases"


class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_INSTALL
        self.name = "安装Github桌面版"
        self.author = '小鱼'

    @staticmethod
    def version_key(version):
        return [int(n) for n in re.findall(r"\d+", version)]

    def latest_deb(self):
        """读镜像的软件包索引, 返回最新版的 (版本号, 下载地址), 失败返回 None"""
        result = CmdTask("wget -qO- -T 15 -t 3 {}/dists/any/main/binary-{}/Packages".format(mwt_mirror, osarch)).run()
        if result[0] != 0:
            return None
        packages, current = [], {}
        for line in result[1] + [""]:
            if not line.strip():
                if "Version" in current and "Filename" in current:
                    packages.append(current)
                current = {}
            elif ":" in line:
                key, value = line.split(":", 1)
                current[key.strip()] = value.strip()
        if len(packages) == 0:
            return None
        latest = max(packages, key=lambda p: self.version_key(p["Version"]))
        return latest["Version"], "{}/{}".format(mwt_mirror, latest["Filename"])

    def install_github(self):
        if osarch != "amd64":
            # 镜像目前只有 amd64 版
            PrintUtils.print_error("国内镜像只提供amd64版本, {}版本请到 {} 手动下载安装".format(osarch, github_releases))
            return False
        PrintUtils.print_info("正在获取GitHub桌面版最新版本~")
        latest = self.latest_deb()
        if latest is None:
            PrintUtils.print_error("获取GitHub桌面版版本信息失败, 请检查网络后重试")
            return False
        version, url = latest
        PrintUtils.print_info("开始下载GitHub桌面版 {}(约120MB)~".format(version))
        CmdTask('sudo wget -T 15 -t 3 {} -O /tmp/github.deb'.format(url), os_command=True).run()
        if CmdTask("dpkg-deb -I /tmp/github.deb").run()[0] != 0:
            PrintUtils.print_error("GitHub桌面版安装包下载失败, 请检查网络后重试")
            CmdTask("rm -rf /tmp/github.deb").run()
            return False
        # 用 apt 装本地包, 缺的依赖会一起装上
        CmdTask('sudo DEBIAN_FRONTEND=noninteractive apt install -y /tmp/github.deb', os_command=True).run()
        CmdTask("rm -rf /tmp/github.deb").run()
        if "install ok installed" not in " ".join(CmdTask("dpkg-query -W -f='${Status}' github-desktop").run()[1]):
            PrintUtils.print_error("GitHub桌面版安装失败, 请把上面的报错信息发到鱼香社区求助: https://fishros.org.cn/forum")
            return False
        PrintUtils.print_success("GitHub桌面版 {} 安装成功, 可以在应用列表里找到 GitHub Desktop~".format(version))
        return True

    def run(self):
        #正式的运行
        return self.install_github()
