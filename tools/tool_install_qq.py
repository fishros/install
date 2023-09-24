# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion, osarch
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_INSTALL
        self.name = "一键安装QQ"
        self.autor = '五柳小生'

    def install_qq(self):
        PrintUtils.print_info("开始根据系统架构，为你下载对应版本的QQ~")
        if osarch == 'arm64':
            CmdTask('sudo wget https://dldir1.qq.com/qqfile/qq/QQNT/b69de82d/linuxqq_3.2.1-17153_arm64.deb -O /tmp/qq.deb',os_command=True).run()
        elif osarch == 'amd64':
            CmdTask('sudo wget https://dldir1.qq.com/qqfile/qq/QQNT/b69de82d/linuxqq_3.2.1-17153_amd64.deb -O /tmp/qq.deb',os_command=True).run()
        else:
            return False
        PrintUtils.print_info("下载完成，接下来为您安装QQ")
        # 安装依赖
        CmdTask("sudo apt-get update")
        CmdTask("sudo apt install libgtk2.0-0")
        # 解压安装包
        CmdTask("sudo dpkg -i /tmp/qq.deb").run()
        CmdTask("rm -rf /tmp/qq.deb").run()
        PrintUtils.print_info("安装完成~")



    def run(self):
        #正式的运行
        self.install_qq()