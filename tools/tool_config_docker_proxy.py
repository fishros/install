# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file



class Tool(BaseTool):
    def __init__(self):
        self.name = "一键配置Docker代理(支持VPN+代理服务两种模式)"
        self.type = BaseTool.TYPE_INSTALL
        self.autor = '小鱼'


    def config_docker_proxy(self):
        

        dic = {1:"VPN模式(需要本地有支持HTTP代理)",2:"服务模式(需要提供支持Docker代理的服务器地址)",3:"删除所有模式代理"}
        code,result = ChooseTask(dic, "请选择代理模式,如果不清楚可以选2").run()
        # 根据系统架构下载不同版本的安装包
        if code==1:
            url = input('请输入代理所在地址(直接回车使用:127.0.0.1):')
            if not url:
                url = '127.0.0.1'
            port = input('请输入代理所在端口:')
            proxy_config_vpn = f"""[Service]
Environment="HTTP_PROXY=http://{url}:{port}/"
Environment="HTTPS_PROXY=http://{url}:{port}/"
Environment="NO_PROXY=localhost,127.0.0.1,{url},.example.com"""
            FileUtils.new('/etc/systemd/system/docker.service.d/','proxy.conf',proxy_config_vpn)
            PrintUtils.print_info(f"在{'/etc/systemd/system/docker.service.d'}/{'proxy.conf'}写入了{proxy_config_vpn},接下来为你重启Docker!")
            CmdTask("sudo systemctl daemon-reload").run()
            CmdTask("sudo systemctl restart docker").run()
        elif code==2:
            url = input('请输入代理网址(直接回车将进入选择界面):')
            if not url:
                dic = {1:"https://dockerpull.com",2:"https://docker.fxxk.dedyn.io",3:"https://ac77d18f43e44819b553040f294b8f9b.mirror.swr.myhuaweicloud.com"}
                code,result = ChooseTask(dic, "请选择代理加速网址").run()
                url = dic[code]
                print(url)
            proxy_config_vpn = f'{{"registry-mirrors": ["{url}"]}}'
            FileUtils.new('/etc/docker/','daemon.json',proxy_config_vpn)
            PrintUtils.print_info(f"在{'/etc/docker/'}/{'daemon.json'}写入了{proxy_config_vpn},接下来为你重启Docker!")
            CmdTask("sudo systemctl daemon-reload").run()
            CmdTask("sudo systemctl restart docker").run()
        elif code==3:
            CmdTask("sudo rm /etc/systemd/system/docker.service.d/proxy.conf").run()
            CmdTask("sudo rm /etc/docker/daemon.json").run()
            CmdTask("sudo systemctl daemon-reload").run()
            CmdTask("sudo systemctl restart docker").run()
        PrintUtils.print_info("配置完成,接下来你可以尝试再次拉取镜像了~")

    def run(self):
        self.config_docker_proxy()

