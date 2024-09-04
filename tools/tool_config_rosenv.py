# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_CONFIG
        self.name = "一键配置ROS开发环境"
        self.autor = '小鱼'
    def config_rosenv(self):
        shell = FileUtils.get_shell()

        def get_source_command(dic):
            choose = 'echo "<tips>?"\nread choose\ncase $choose in\n'
            tips = "ros:"
            count = 0
            for i in range(len(dic)):
                count += 1
                choose += "{}) source  {};;\n".format(count,dic[i])
                tips += dic[i].replace("/opt/ros/","").replace(f"/setup.{shell}","")+"("+str(count)+") "
            return choose.replace('<tips>', tips)+"esac"

        # check and append source 
        result = CmdTask(f"ls /opt/ros/*/setup.{shell}", 0).run()
        shellrc_result = CmdTask(f"ls /home/*/.{shell}rc", 0).run() 
        if shellrc_result[0]!=0:  shellrc_result = CmdTask(f"ls /root/.{shell}rc", 0).run() 
        if len(result[1])>1:
            PrintUtils.print_info(f'检测到系统有多个ROS环境,已为您配置未启动终端选择,修改~/.{shell}rc可关闭')
            data = get_source_command(result[1])
            for shellrc in shellrc_result[1]:
                FileUtils.find_replace(shellrc,f"source\s+/opt/ros/[A-Za-z]+/setup.{shell}","")
                FileUtils.find_replace_sub(shellrc,"# >>> fishros initialize >>>","# <<< fishros initialize <<<", "")
                FileUtils.append(shellrc,"# >>> fishros initialize >>>\n"+data+"\n# <<< fishros initialize <<<\n")
            return True
        elif len(result[1])==1 and len(result[1][0])>2:
            PrintUtils.print_info(f'检测到系统有1个ROS环境,已为您配置未启动终端自动激活,修改~/.{shell}rc可关闭')
            for shellrc in shellrc_result[1]:
                FileUtils.find_replace(shellrc,f"source\s+/opt/ros/[A-Za-z]+/setup.{shell}","")
                FileUtils.find_replace_sub(shellrc,"# >>> fishros initialize >>>","# <<< fishros initialize <<<", "")
                FileUtils.append(shellrc,'# >>> fishros initialize >>>\n source {} \n# <<< fishros initialize <<<\n'.format(result[1][0]))
            return True
        else:
            PrintUtils.print_error("当前系统并没有安装ROS，请使用一键安装安装~")
            return False
            

    def run(self):
        self.config_rosenv()
