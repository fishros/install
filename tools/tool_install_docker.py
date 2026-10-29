# -*- coding: utf-8 -*-
import os
from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, AptUtils, ChooseTask
from .base import osversion, osarch
from .base import run_tool_file

# 按顺序尝试, 哪个镜像的公钥能下下来就用哪个镜像的软件源(公钥和源要来自同一处)
docker_mirrors = [
    "https://mirrors.tuna.tsinghua.edu.cn/docker-ce",
    "https://mirrors.ustc.edu.cn/docker-ce",
    "https://mirrors.aliyun.com/docker-ce",
]
docker_key = "/etc/apt/keyrings/docker.asc"
docker_list = "/etc/apt/sources.list.d/docker.list"


class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装Docker，支持amd64和arm64架构系统"
        self.type = BaseTool.TYPE_INSTALL
        self.author = 'alyssa'

    @staticmethod
    def key_ok():
        try:
            with open(docker_key, "r") as f:
                return "BEGIN PGP PUBLIC KEY BLOCK" in f.read()
        except Exception:
            return False

    def remove_broken_source(self):
        """
        上次公钥没下载成功时会留下一个没有公钥的 docker.list, 之后每次 apt update 都报 NO_PUBKEY,
        下面的 checkapt 也会因此失败直接退出, 用户自己很难看出原因, 所以先清掉
        """
        if os.path.exists(docker_list) and not self.key_ok():
            PrintUtils.print_warn("检测到上次没装好留下的Docker软件源(缺少公钥), 先清理掉再重新安装~")
            CmdTask("sudo rm -f {}".format(docker_list)).run()

    def download_key(self):
        """依次从各镜像下载公钥, 返回下载成功的镜像地址, 都失败返回 None"""
        for mirror in docker_mirrors:
            CmdTask('curl -fsSL --retry 3 --connect-timeout 15 --max-time 60 "{}/linux/ubuntu/gpg" -o {}'.format(mirror, docker_key)).run()
            if self.key_ok():
                CmdTask('chmod a+r {}'.format(docker_key)).run()
                return mirror
            PrintUtils.print_warn("从{}下载Docker公钥失败, 换下一个镜像试试~".format(mirror))
        CmdTask("sudo rm -f {}".format(docker_key)).run()
        return None

    def install_docker(self):
        """
        Executing Docker install script with updated commands for new installation steps.
        """
        PrintUtils.print_info("开始根据系统架构,为你下载对应版本的docker~")
        if osarch not in ('amd64', 'arm64'):
            PrintUtils.print_error("暂不支持当前系统架构:{}, 目前只支持amd64和arm64".format(osarch))
            return False

        self.remove_broken_source()
        # Check if apt is available
        if not AptUtils.checkapt():
            return False

        # Pre-installation steps
        CmdTask('DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates curl ', 120, os_command=True).run()
        CmdTask('install -m 0755 -d /etc/apt/keyrings', 10, os_command=True).run()

        # Add Docker GPG key
        mirror = self.download_key()
        if mirror is None:
            PrintUtils.print_error("Docker公钥下载失败, 请检查网络后重试")
            return False

        # Add Docker repository
        CmdTask('echo "deb [arch={} signed-by={}] {}/linux/ubuntu $(lsb_release -cs) stable" > {}'.format(
            osarch, docker_key, mirror, docker_list), os_command=True).run()

        # Update apt index and install Docker
        PrintUtils.print_info("下载完成,接下来升级apt索引~")
        if CmdTask('apt-get update', 120).run()[0] != 0:
            # 源加上了却更新不了时撤掉, 免得影响之后所有 apt 操作
            PrintUtils.print_error("Docker软件源更新失败, 已撤销添加的软件源, 请检查网络后重试")
            CmdTask("sudo rm -f {} {}".format(docker_list, docker_key)).run()
            return False
        PrintUtils.print_info("开始安装最新版本docker CE~")
        CmdTask('DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-ce-rootless-extras docker-buildx-plugin', 120,os_command=True).run()

        result = CmdTask('docker --version').run()
        if result[0] != 0:
            PrintUtils.print_error("Docker安装失败, 请把上面的报错信息发到鱼香社区求助: https://fishros.org.cn/forum")
            return False

        # Post-installation steps
        CmdTask('sudo groupadd -f docker', 10,os_command=True).run()
        users = FileUtils.getusers()
        for user in users:
            CmdTask('sudo gpasswd -a {} docker'.format(user), 10,os_command=True).run()

        PrintUtils.print_success("Docker安装成功: {}".format(" ".join(result[1])))
        PrintUtils.print_info("当前用户需要重新登录(或重启)后才能不加sudo使用docker命令~")
        return True

    def run(self):
        return self.install_docker()
