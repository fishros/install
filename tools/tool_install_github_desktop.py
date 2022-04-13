# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_INSTALL
        self.name = "安装Github桌面版"
        self.autor = '小鱼'

    def install_github(self):
        """
        wget https://mirror.ghproxy.com/https://github.com/shiftkey/desktop/releases/download/release-2.9.12-linux4/GitHubDesktop-linux-2.9.12-linux4.deb -O /tmp/github.deb
        sudo dpkg -i  /tmp/github.deb
        sudo apt install /tmp/github.deb -y
        """
        CmdTask('sudo wget https://mirror.ghproxy.com/https://github.com/shiftkey/desktop/releases/download/release-2.9.12-linux4/GitHubDesktop-linux-2.9.12-linux4.deb -O /tmp/github.deb',os_command=True).run()
        CmdTask('sudo dpkg -i  /tmp/github.deb').run()
        CmdTask('sudo apt install /tmp/github.deb -y').run()

    def run(self):
        #正式的运行
        self.install_github()
