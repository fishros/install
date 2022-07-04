# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装Docker，支持amd64和arm64架构系统"
        self.type = BaseTool.TYPE_INSTALL
        self.autor = 'alyssa'

    def install_docker(self):
        PrintUtils.print_info("开始根据系统架构,为你下载对应版本的docker~")

        # 更换系统源
        # dic = {1:"更换系统源再继续安装",2:"不更换继续安装"}
        # code,result = ChooseTask(dic, "如果您是第一次安装，推荐您先更换一下系统源").run()
        # if code==1: 
        #     run_tool_file('tools.tool_config_system_source')

        # check apt
        if not AptUtils.checkapt(): return False

        #pre-install
        CmdTask('sudo apt install apt-transport-https ca-certificates curl software-properties-common -y',120).run()

        #add key
        CmdTask('curl -fsSL https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/gpg | sudo apt-key add -',10).run()
        #verify key
        CmdTask('sudo apt-key fingerprint 0EBFCD88',10).run()

        # 根据系统架构下载不同版本的安装包
        if osarch=='amd64':
            CmdTask('sudo add-apt-repository "deb [arch=amd64] https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu $(lsb_release -cs) stable" -y',os_command=True).run()
        elif osarch=='arm64':
            CmdTask('sudo add-apt-repository "deb [arch=arm64] https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu $(lsb_release -cs) stable" -y',os_command=True).run()
        else:
            return False
        PrintUtils.print_info("下载完成,接下来升级apt索引~")
        CmdTask("sudo apt update").run()
        PrintUtils.print_info("开始安装最新版本docker CE~")
        CmdTask("sudo apt --fix-broken install -y").run()
        # CmdTask("sudo apt install docker-ce -y").run()
        AptUtils.install_pkg_check_dep("docker-ce")
        CmdTask("sudo groupadd docker").run()
        user = FileUtils.getusers()[0]
        CmdTask("sudo gpasswd -a {} docker".format(user)).run()
        # CmdTask("newgrp docker",os_command=True).run()

        PrintUtils.print_info("安装完成,接下来你可以尝试使用docker --version指令测试是有正常回显~")

    def run(self):
        self.install_docker()

