# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file

# 微软官方的「最新稳定版」地址, 会 302 跳到国内也能访问的 CDN(vscode.download.prss.microsoft.com)
# 原来写死 1.86.2(2024-02), 改成每次装最新版
vscode_latest_url = "https://update.code.visualstudio.com/latest/linux-deb-{}/stable"
vscode_arch = {'amd64': 'x64', 'arm64': 'arm64', 'armhf': 'armhf'}

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装Vscode"
        self.type = BaseTool.TYPE_INSTALL
        self.author = '小鱼'

    def install_vscode(self):
        PrintUtils.print_info("开始根据系统架构,为你下载对应版本的vscode~")
        # 根据系统架构下载不同版本的安装包
        if osarch not in vscode_arch:
            PrintUtils.print_error("暂不支持当前系统架构:{}".format(osarch))
            return False
        CmdTask('sudo wget -T 15 -t 3 {} -O /tmp/vscode.deb'.format(vscode_latest_url.format(vscode_arch[osarch])),os_command=True).run()
        if CmdTask("dpkg-deb -I /tmp/vscode.deb").run()[0] != 0:
            PrintUtils.print_error("VSCode安装包下载失败, 请检查网络后重试")
            CmdTask("rm -rf /tmp/vscode.deb").run()
            return False
        PrintUtils.print_info("下载完成,接下来为你安装Vscode~")
        # 用 apt 装本地包, 缺依赖时会一起装上(dpkg -i 缺依赖就直接失败)
        CmdTask("sudo DEBIAN_FRONTEND=noninteractive apt install -y /tmp/vscode.deb", os_command=True).run()
        CmdTask("rm -rf /tmp/vscode.deb").run()
        result = CmdTask("dpkg-query -W -f='${Status} ${Version}' code").run()
        status = " ".join(result[1])
        if result[0] != 0 or "install ok installed" not in status:
            PrintUtils.print_error("VSCode安装失败, 请把上面的报错信息发到鱼香社区求助: https://fishros.org.cn/forum")
            return False
        PrintUtils.print_success("VSCode安装成功, 版本: {}".format(status.replace("install ok installed", "").strip()))
        return True

    def run(self):
        return self.install_vscode()
