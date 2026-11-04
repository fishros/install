# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask,DockerUtils
from .base import osversion,osarch
from .base import run_tool_file



class Tool(BaseTool):
    def __init__(self):
        self.name = "一键配置Docker代理(支持VPN+代理服务两种模式)"
        self.type = BaseTool.TYPE_INSTALL
        self.author = '小鱼'


    def config_docker_proxy(self):
        

        dic = {1:"VPN模式(需要本地有支持HTTP代理)",2:"服务模式(需要提供支持Docker代理的服务器地址)",3:"删除所有模式代理"}
        code,result = ChooseTask(dic, "请选择代理模式,如果不清楚可以选2").run()
        if code==0:
            return BaseTool.BACK
        if code==1:
            url = input('请输入代理所在地址(直接回车使用:127.0.0.1):')
            if not url:
                url = '127.0.0.1'
            port = input('请输入代理所在端口:')
            proxy_config_vpn = """[Service]
Environment="HTTP_PROXY=http://{}:{}/"
Environment="HTTPS_PROXY=http://{}:{}/"
Environment="NO_PROXY=localhost,127.0.0.1,{},.example.com""".format(url, port, url, port, url)
            FileUtils.new('/etc/systemd/system/docker.service.d/','proxy.conf',proxy_config_vpn)
            PrintUtils.print_info("在{}/{}写入了{},接下来为你重启Docker!".format('/etc/systemd/system/docker.service.d', 'proxy.conf', proxy_config_vpn))
            CmdTask("sudo systemctl daemon-reload").run()
            CmdTask("sudo systemctl restart docker").run()
        elif code==2:
            # 原来的 dockerpull.com / docker.fxxk.dedyn.io 已失效, 只保留华为云加速, 回车直接用它
            url = input('请输入代理网址(直接回车使用华为云加速):').strip()
            if not url:
                url = DockerUtils.registry_mirror
            PrintUtils.print_info("在{}写入加速地址{}, 接下来为你重启Docker!".format(DockerUtils.daemon_json, url))
            DockerUtils.set_registry_mirror(url)
        elif code==3:
            CmdTask("sudo rm /etc/systemd/system/docker.service.d/proxy.conf").run()
            CmdTask("sudo rm /etc/docker/daemon.json").run()
            CmdTask("sudo systemctl daemon-reload").run()
            CmdTask("sudo systemctl restart docker").run()
        PrintUtils.print_info("配置完成,接下来你可以尝试再次拉取镜像了~")

    def run(self):
        return self.config_docker_proxy()

