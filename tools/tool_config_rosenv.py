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
        def get_source_command(dic):
            choose = 'echo "<tips>?"\nread choose\ncase $choose in\n'
            tips = "ros:"
            count = 0
            for i in range(len(dic)):
                count += 1
                choose += "{}) source  {};;\n".format(count,dic[i])
                tips += dic[i].replace("/opt/ros/","").replace("/setup.bash","")+"("+str(count)+") "
            return choose.replace('<tips>', tips)+"esac"

        # check and append source 
        result = CmdTask("ls /opt/ros/*/setup.bash", 0).run()
        bashrc_result = CmdTask("ls /home/*/.bashrc", 0).run() 
        if bashrc_result[0]!=0:  bashrc_result = CmdTask("ls /root/.bashrc", 0).run() 
        if len(result[1])>1:
            PrintUtils.print_info('检测到系统有多个ROS环境,已为你生成启动选择,修改~/.bashrc可关闭')
            data = get_source_command(result[1])
            for bashrc in bashrc_result[1]:
                FileUtils.find_replace(bashrc,"source\s+/opt/ros/[A-Za-z]+/setup.bash","")
                FileUtils.find_replace_sub(bashrc,"# >>> fishros initialize >>>","# <<< fishros initialize <<<", "")
                FileUtils.append(bashrc,"# >>> fishros initialize >>>\n"+data+"\n# <<< fishros initialize <<<\n")
            return True
        elif len(result[1])==1 and len(result[1][0])>2:
            PrintUtils.print_info('检测到系统有1个ROS环境,已为你生成启动选择,修改~/.bashrc可关闭')
            for bashrc in bashrc_result[1]:
                FileUtils.find_replace(bashrc,"source\s+/opt/ros/[A-Za-z]+/setup.bash","")
                FileUtils.find_replace_sub(bashrc,"# >>> fishros initialize >>>","# <<< fishros initialize <<<", "")
                FileUtils.append(bashrc,'# >>> fishros initialize >>>\n source {} \n# <<< fishros initialize <<<\n'.format(result[1][0]))
            return True
        else:
            PrintUtils.print_error("当前系统并没有安装ROS，请使用一键安装安装~")
            return False
            

    def run(self):
        self.config_rosenv()
