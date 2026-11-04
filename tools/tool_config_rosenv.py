# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file
import os

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_CONFIG
        self.name = "一键配置ROS开发环境"
        self.author = '小鱼'

    def config_rosenv(self):
        shell = FileUtils.get_shell()

        def get_source_command(dic):
            choose = 'echo "<tips>?"\nread choose\ncase $choose in\n'
            tips = "ros:"
            count = 0
            for i in range(len(dic)):
                count += 1
                choose += "{}) source  {};;\n".format(count,dic[i])
                tips += dic[i].replace("/opt/ros/","").replace("/setup.{}".format(shell),"")+"("+str(count)+") "
            return choose.replace('<tips>', tips)+"esac"

        # check and append source 
        result = CmdTask("ls /opt/ros/*/setup.{}".format(shell), 0).run()
        ros_count = len(result[1])
        ros_sourcefile = result[1]
        if ros_count==0:
            PrintUtils.print_error("当前系统并没有安装ROS，请使用一键安装安装~")
            return False
        
        usershomes = FileUtils.getusershome()
        shell_file = ".{}rc".format(shell)
        for userhome in usershomes:
            shell_path = os.path.join(userhome,shell_file)
            PrintUtils.print_delay('正在准备配置用户目录:{}'.format(shell_path))
            if FileUtils.exists(shell_path):
                PrintUtils.print_info('当前系统包含{}个ROS,已为您完成启动终端自动激活ROS环境,修改{}可关闭'.format(ros_count,shell_path))
                if ros_count>1:
                    data = get_source_command(ros_sourcefile)
                else:
                    data = 'source {}'.format(ros_sourcefile[0])
                FileUtils.find_replace(shell_path,"source\s+/opt/ros/[A-Za-z]+/setup.{}".format(shell),"") # 删除旧source
                FileUtils.find_replace_sub(shell_path,"# >>> fishros initialize >>>","# <<< fishros initialize <<<", "") # 替换
                FileUtils.append(shell_path,"# >>> fishros initialize >>>\n"+data+"\n# <<< fishros initialize <<<\n") # 添加
            PrintUtils.print_text("")

    def fix_rosidl_non_ascii_path(self):
        """
        ROS2 的 rosidl_adapter 用 CMake 的 file(STRINGS) 读回接口列表时没指定 UTF-8, CMake 会把中文等非 ASCII
        字符当作分隔符丢掉: 工作空间放在 ~/桌面 这类中文路径下, colcon build 编译消息包就报
        "rosidl_generate_interfaces ... list index: 1 out of range" / "Target dependency ... .idl does not exist".
        上游 humble/jazzy/rolling 都没修, 这里给已装的 ROS2 补上 ENCODING UTF-8; ROS 升级覆盖后再运行一次本工具即可
        """
        import glob
        old = 'idl_output}" idl_tuples)'
        for path in glob.glob("/opt/ros/*/share/rosidl_adapter/cmake/rosidl_adapt_interfaces.cmake"):
            with open(path) as f:
                if old not in f.read():
                    continue
            CmdTask(
                "sudo sed -i.fishros-bak 's#{}#idl_output}}\" idl_tuples ENCODING UTF-8)#' {}".format(old, path), 10
            ).run()
            with open(path) as f:
                if "idl_tuples ENCODING UTF-8)" in f.read():
                    PrintUtils.print_success("已修复 {} 在中文路径下编译消息包报错的问题".format(path.split("/")[3]))

    def run(self):
        self.config_rosenv()
        self.fix_rosidl_non_ascii_path()
