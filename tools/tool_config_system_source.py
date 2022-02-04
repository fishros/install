# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_CONFIG
        self.name = "模板工程"
        self.autor = '小鱼'


    def change_source(self):
        """
        一键换源
        """
        ports = u"""
            deb https://mirrors.ustc.edu.cn/ubuntu-ports/ <code-name> main restricted universe multiverse
            deb https://mirrors.ustc.edu.cn/ubuntu-ports/ <code-name>-updates main restricted universe multiverse
            deb https://mirrors.ustc.edu.cn/ubuntu-ports/ <code-name>-backports main restricted universe multiverse
            deb https://mirrors.ustc.edu.cn/ubuntu-ports/ <code-name>-security main restricted universe multiverse
        """
        normal = """
            deb https://mirrors.ustc.edu.cn/ubuntu/ <code-name> main restricted universe multiverse
            deb https://mirrors.ustc.edu.cn/ubuntu/ <code-name>-updates main restricted universe multiverse
            deb https://mirrors.ustc.edu.cn/ubuntu/ <code-name>-backports main restricted universe multiverse
            deb https://mirrors.ustc.edu.cn/ubuntu/ <code-name>-security main restricted universe multiverse
        """
        PrintUtils.print_delay('欢迎使用一键换源工具，本工具由[鱼香ROS]小鱼贡献..')
        # delete file
        dic = {1:"仅更换系统源",2:"更换系统源并清理第三方源"}
        code,result = ChooseTask(dic, "请选择换源方式").run()
        FileUtils.delete('/etc/apt/sources.list')
        if code==2: 
            print("删除一个资源文件")
            FileUtils.delete('/etc/apt/sources.list.d')
        # check sys version
        arch = AptUtils.getArch()
        PrintUtils.print_delay('检测到当前系统架构为[{}],正在为你更换对应源..'.format(arch))
        if arch=='amd64': FileUtils.new('/etc/apt/','sources.list',normal.replace("<code-name>",osversion.get_codename()))
        else: FileUtils.new('/etc/apt/','sources.list',ports.replace("<code-name>",osversion.get_codename()))
        # update
        PrintUtils.print_delay("替换完成，尝试第一次更新....")
        result = CmdTask('sudo apt update',100).run()
        # https error update second
        if result[0]!= 0 and FileUtils.check_result(result[1]+result[2],['Certificate verification','证书']):
            PrintUtils.print_delay("发生证书错误，尝试第二次更新....")
            FileUtils.delete('/etc/apt/sources.list')
            if arch=='amd64': FileUtils.new('/etc/apt/','sources.list',normal.replace("https://","http://").replace("<code-name>",osversion.get_codename()))
            else: FileUtils.new('/etc/apt/','sources.list',ports.replace("https://","http://").replace("<code-name>",osversion.get_codename()))
            result = CmdTask('sudo apt update',100).run()
        # final check
        if result[0]==0: 
            PrintUtils.print_success("搞定了,不信你看,累死宝宝了，还不快去给小鱼点个赞~")
            PrintUtils.print_info(result[1])
        PrintUtils.print_success("镜像修复完成.....")


    def run(self):
        #正式的运行
        self.change_source()
