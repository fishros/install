# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_INSTALL
        self.name = "一键安装系统自带ROS，仅在Ubuntu 22.04 及以上版本系统中使用。"
        self.autor = 'Elysia'

    def run(self):
        #正式的运行
        self.check_sys_source()
        self.install_system_ros()
        return True

    def check_sys_source(self):
        # 更换系统源
        dic = {1:"更换系统源再继续安装",2:"不更换继续安装"}
        PrintUtils.print_warn("=========接下来这一步很很很很重要，如果不知道怎么选请选择1========")
        code,result = ChooseTask(dic, "新手或首次安装一定要一定要一定要换源并清理三方源，换源!!!系统默认国外源容易失败!!").run()
        if code==1: 
            tool = run_tool_file('tools.tool_config_system_source',autorun=False)
            tool.change_sys_source()

    def install_system_ros(self):
        version_dic = {1:"完整版",2:"基础版(小)"}
        code,name = ChooseTask(version_dic,"请选择安装的具体版本(如果不知道怎么选,请选1桌面版):",False).run()

        if code==0: 
            print("你选择退出。。。。")
            return

        install_tool = 'aptitude'
        install_tool_apt = 'apt'
        if osversion.get_version() == "16.04":
            install_tool = 'apt'

        if install_tool=='aptitude':
            AptUtils.install_pkg('aptitude')
            AptUtils.install_pkg('aptitude')

        # 先尝试使用apt 安装，之后再使用aptitude。
        if code==2:
            # 第一次尝试
            cmd_result = CmdTask("sudo {} install  {} -y".format(install_tool_apt,"ros-base-dev"),300,os_command=True).run()
            cmd_result = CmdTask("sudo {} install  {} -y".format(install_tool_apt,"ros-base-dev"),300,os_command=False).run()
            if FileUtils.check_result(cmd_result,['未满足的依赖关系','unmet dependencies','but it is not installable']):
                # 尝试使用aptitude解决依赖问题
                PrintUtils.print_warn("============================================================")
                PrintUtils.print_delay("请注意我，检测你在安装过程中出现依赖问题，请在稍后输入n,再选择y,即可解决")
                import time
                input("确认了解情况，请输入回车继续安装")
                cmd_result = CmdTask("sudo {} install   {} ".format(install_tool,"ros-base-dev"),300,os_command=True).run()
                cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool,"ros-base-dev"),300,os_command=False).run()
        
        elif code==1:
            cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool_apt,"ros-desktop-full-dev"),300,os_command=True).run()
            cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool_apt,"ros-desktop-full-dev"),300,os_command=False).run()
            if FileUtils.check_result(cmd_result,['未满足的依赖关系','unmet dependencies','but it is not installable']):
                # 尝试使用aptitude解决依赖问题
                PrintUtils.print_warn("============================================================")
                PrintUtils.print_delay("请注意我，检测你在安装过程中出现依赖问题，请在稍后输入n,再选择y,即可解决（若无法解决，清在稍后手动运行命令: sudo aptitude install {})".format(RosVersions.get_desktop_version(install_version)))
                import time
                input("确认了解情况，请输入回车继续安装")
                cmd_result = CmdTask("sudo {} install   {}".format(install_tool,"ros-desktop-full-dev"),300,os_command=True).run()
                cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool,"ros-desktop-full-dev"),300,os_command=False).run()

        # apt broken error
        if cmd_result[0]!=0:
            if FileUtils.check_result(cmd_result[1]+cmd_result[2],['sudo apt --fix-broken install -y']):
                if code==2: cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool,"ros-base-dev"),300,os_command=False).run()
                elif code==1: cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool,"ros-desktop-full-dev"),300,os_command=False).run()

        return True
