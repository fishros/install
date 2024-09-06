# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, AptUtils, ChooseTask
from .base import osversion, osarch
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装Docker，支持amd64和arm64架构系统"
        self.type = BaseTool.TYPE_INSTALL
        self.author = 'alyssa'

    def install_docker(self):
        """
        Executing Docker install script with updated commands for new installation steps.
        """
        PrintUtils.print_info("开始根据系统架构,为你下载对应版本的docker~")

        # Check if apt is available
        if not AptUtils.checkapt():
            return False

        # Pre-installation steps
        CmdTask('apt-get update', 120, os_command=True).run()
        CmdTask('DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates curl ', 120, os_command=True).run()
        CmdTask('install -m 0755 -d /etc/apt/keyrings', 10, os_command=True).run()

        # Add Docker GPG key
        CmdTask('curl -fsSL "https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/ubuntu/gpg" -o /etc/apt/keyrings/docker.asc', 10, os_command=True).run()
        CmdTask('chmod a+r /etc/apt/keyrings/docker.asc', 10,os_command=True).run()

        # Add Docker repository
        if osarch == 'amd64':
            CmdTask('echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list', os_command=True).run()
        elif osarch == 'arm64':
            CmdTask('echo "deb [arch=arm64 signed-by=/etc/apt/keyrings/docker.asc] https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list', os_command=True).run()
        else:
            return False

        # Update apt index and install Docker
        PrintUtils.print_info("下载完成,接下来升级apt索引~")
        CmdTask('apt-get update ', 10,os_command=True).run()
        PrintUtils.print_info("开始安装最新版本docker CE~")
        CmdTask('DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-ce-rootless-extras docker-buildx-plugin', 120,os_command=True).run()

        # Post-installation steps
        CmdTask('sudo groupadd docker', 10,os_command=True).run()
        user = FileUtils.getusers()[0]
        CmdTask('sudo gpasswd -a {} docker'.format(user), 10,os_command=True).run()

        PrintUtils.print_info("安装完成,接下来你可以尝试使用docker --version指令测试是有正常回显~")

    def run(self):
        self.install_docker()
