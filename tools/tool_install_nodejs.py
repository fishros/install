# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装nodejs并配置环境"
        self.type = BaseTool.TYPE_INSTALL
        self.autor = '小鱼'

    def install_nodejs(self):
        PrintUtils.print_info("开始根据系统架构,为你下载对应版本的nodejs~")
        # 根据系统架构下载不同版本的安装包
        if osarch=='amd64':
            CmdTask('wget https://npmmirror.com/mirrors/node/v16.13.2/node-v16.13.2-linux-x64.tar.xz -O /tmp/nodejs.tar.xz',os_command=True).run()
        elif osarch=='arm64':
            CmdTask('wget https://npmmirror.com/mirrors/node/v16.13.2/node-v16.13.2-linux-arm64.tar.xz -O /tmp/nodejs.tar.xz',os_command=True).run()
        else:
            return False
        PrintUtils.print_info("下载完成,接下来为你解压安装Nodejs~")
        CmdTask("rm -rf /opt/nodejs/").run()
        CmdTask("mkdir -p /opt/nodejs/").run()
        CmdTask("sudo apt install xz-utils -y").run()
        CmdTask("sudo tar -xvf /tmp/nodejs.tar.xz  -C /opt/nodejs/").run()
        CmdTask("sudo chmod -R 777 /opt/nodejs/").run()
        CmdTask("rm -rf /tmp/nodejs.tar.xz").run()
        PrintUtils.print_info("解压完成,接下来为你配置nodejs环境~")
        # 配置环境
        for bashrc in FileUtils.getbashrc():
            FileUtils.find_replace_sub(bashrc,"# >>> nodejs initialize >>>","# <<< nodejs initialize <<<", "")
            FileUtils.append(bashrc,"# >>> nodejs initialize >>>\n"+"export PATH=$PATH:/opt/nodejs/node-v16.13.2-linux-x64/bin/"+"\n# <<< nodejs initialize <<<")
        PrintUtils.print_info("配置完成,接下来你可以尝试使用node和npm指令运行了~")

    def run(self):
        self.install_nodejs()

