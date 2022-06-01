# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装Code-Server"
        self.type = BaseTool.TYPE_INSTALL
        self.autor = '小鱼'

    def install_code_server(self):
        PrintUtils.print_info("开始根据系统架构,为你下载对应版本的Code-Server~")
        # 根据系统架构下载不同版本的安装包
        if osarch=='amd64':
            CmdTask('sudo wget https://github.com/coder/code-server/releases/download/v4.4.0/code-server_4.4.0_amd64.deb -O /tmp/code-server.deb',os_command=True).run()
        elif osarch=='arm64':
            CmdTask('sudo wget https://github.com/coder/code-server/releases/download/v4.4.0/code-server_4.4.0_arm64.deb -O /tmp/code-server.deb',os_command=True).run()
        else:
            return False
        PrintUtils.print_info("下载完成,接下来为你安装Code-Server~")
        CmdTask("sudo dpkg -i /tmp/code-server").run()
        CmdTask("rm -rf /tmp/code-server").run()
        PrintUtils.print_info("安装完成~")

    def run(self):
        self.install_code_server()

