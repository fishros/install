# -*- coding: utf-8 -*-
from distutils import cmd
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装ROS和ROS2,支持树莓派Jetson"
        self.type = BaseTool.TYPE_INSTALL
        self.autor = '小鱼'

    def install_ros(self):
        """
        一键装ROS/ROS2
        """
        ros_mirror_dic = {
            "tsinghua":{"ROS1":"http://mirrors.tuna.tsinghua.edu.cn/ros/ubuntu/","ROS2":"http://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu/"},
            "huawei":{"ROS1":"https://repo.huaweicloud.com/ros/ubuntu/","ROS2":"https://repo.huaweicloud.com/ros2/ubuntu/"},
            "packages.ros":{"ROS1":"http://packages.ros.org/ros/ubuntu/","ROS2":"http://packages.ros.org/ros2/ubuntu/"},
            "repo-ros2":{"ROS2":"http://repo.ros2.org/ubuntu/"}
        }

        ros_dist_dic = {
            'artful':{"packages.ros"},
            'bionic':{"tsinghua","huawei","packages.ros"},
            'buster':{"tsinghua","huawei","packages.ros"},
            'cosmic':{"packages.ros"},
            'disco':{"packages.ros"},
            'eoan':{"packages.ros"},
            'focal':{"tsinghua","huawei","packages.ros"},
            'jessie':{"tsinghua","huawei","packages.ros"},
            'lucid':{"packages.ros"},
            'maverick':{"packages.ros"},
            'natty':{"packages.ros"},
            'oneiric':{"packages.ros"},
            'precise':{"packages.ros"},
            'quantal':{"packages.ros"},
            'raring':{"packages.ros"},
            'saucy':{"packages.ros"},
            'stretch':{"tsinghua","huawei","packages.ros"},
            'trusty':{"tsinghua","huawei","packages.ros"},
            'utopic':{"packages.ros"},
            'vivid':{"packages.ros"},
            'wheezy':{"packages.ros"},
            'wily':{"packages.ros"},
            'xenial':{"tsinghua","huawei","packages.ros"},
            'yakkety':{"packages.ros"},
            'zesty':{"packages.ros"},
        }

        ros2_dist_dic = {
            'bionic':{"tsinghua","huawei","packages.ros"},
            'bullseye':{"tsinghua","huawei","packages.ros"},
            'buster':{"tsinghua","huawei","packages.ros"},
            'cosmic':{"tsinghua","huawei","packages.ros"},
            'disco':{"tsinghua","huawei","packages.ros"},
            'eoan':{"tsinghua","huawei","packages.ros"},
            'focal':{"tsinghua","huawei","packages.ros"},
            'jessie':{"tsinghua","huawei"},
            'jammy':{"packages.ros"},
            'stretch':{"tsinghua","huawei","packages.ros"},
            'trusty':{"tsinghua","huawei"},
            'xenial':{"tsinghua","huawei","packages.ros"},
        }


        def get_mirror_by_code(code):
            mirror = []
            if "tsinghua" in ros_dist_dic[code]:
                mirror.append(ros_mirror_dic["tsinghua"]['ROS1'])
            elif "huawei" in ros_dist_dic[code]:
                mirror.append(ros_mirror_dic["huawei"]['ROS1'])
            elif "packages.ros" in ros_dist_dic[code]:
                mirror.append(ros_mirror_dic["packages.ros"]['ROS1'])

            if "tsinghua" in ros2_dist_dic[code]:
                mirror.append(ros_mirror_dic["tsinghua"]['ROS2'])
            elif "huawei" in ros2_dist_dic[code]:
                mirror.append(ros_mirror_dic["huawei"]['ROS2'])
            elif "packages.ros" in ros2_dist_dic[code]:
                mirror.append(ros_mirror_dic["packages.ros"]['ROS2'])
            return mirror

        tips = '欢迎使用ROS开箱子工具，本工具由[鱼香ROS]小鱼贡献..'
        PrintUtils.print_delay(tips)

        # check support
        if (osversion.get_codename() not in ros_dist_dic.keys()) or (osversion.get_codename() not in ros2_dist_dic.keys()):
            PrintUtils.print_error("小鱼:检测当前系统{}{}:{} 暂不支持一键安装ROS,请关注公众号《鱼香ROS》获取帮助.".format(osversion.get_name(), osversion.get_version(),osversion.get_codename()))
            return False
        PrintUtils.print_success("小鱼:检测当前系统{}{}:{} 支持一键安装ROS".format(osversion.get_name(), osversion.get_version(),osversion.get_codename()))

        # 更换系统源
        dic = {1:"更换系统源再继续安装",2:"不更换继续安装"}
        code,result = ChooseTask(dic, "如果您是第一次安装，推荐您先更换一下系统源").run()
        if code==1: 
            run_tool_file('tools.tool_config_system_source')


        # check apt
        if not AptUtils.checkapt(): return False

        # pre-install
        cmd_result = CmdTask("sudo apt install curl gnupg2 -y",120).run()

        # add key
        cmd_result = CmdTask("curl -s https://gitee.com/ohhuo/rosdistro/raw/master/ros.asc | sudo apt-key add -",10).run()
        if cmd_result[0]!=0:
            cmd_result = CmdTask("curl -s https://gitee.com/ohhuo/rosdistro/raw/master/ros.asc | sudo apt-key add -",10).run()
        if cmd_result[0]!=0:
            PrintUtils.print_info("导入密钥失败，开始更换导入方式并二次尝试...")
            cmd_result = CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F42ED6FBAB17C654",10).run()


        #add source 
        mirrors = get_mirror_by_code(osversion.get_codename())
        # print("----------------------------",mirrors)
        print(mirrors)
        arch = AptUtils.getArch()
        if arch==None: return False
        source_data = ''
        for mirror in mirrors:
            source_data += 'deb [arch={}]  {} {} main\n'.format(arch,mirror,osversion.get_codename())
        FileUtils.delete('/etc/apt/sources.list.d/ros-fish.list')
        FileUtils.new('/etc/apt/sources.list.d/',"ros-fish.list",source_data)
        # update
        if not AptUtils.checkapt(): PrintUtils.print_error("换源后更新失败，请联系小鱼处理!") 

        # get ros pkgs
        dic_base = AptUtils.search_package('ros-base','ros-[A-Za-z]+-ros-base',"ros-","-base")
        if dic_base== None: return False
        ros_name = []
        for a in dic_base.keys(): ros_name.append(a)
        _,rosname = ChooseTask(ros_name,"请选择你要安装的ROS版本名称:",True).run()
        version_dic = {1:rosname+"完全版",2:rosname+"基础版(小)"}
        code,name = ChooseTask(version_dic,"请选择安装的具体版本:",False).run()
        # install
        if code==2:
            cmd_result = CmdTask("sudo apt install {} -y".format(dic_base[rosname]),300,os_command=True).run()
            cmd_result = CmdTask("sudo apt install {} -y".format(dic_base[rosname]),300,os_command=False).run()
        elif code==1:
            cmd_result = CmdTask("sudo apt install ros-{}-desktop -y".format(rosname),300,os_command=True).run()
            cmd_result = CmdTask("sudo apt install ros-{}-desktop -y".format(rosname),300,os_command=False).run()
        # apt broken error
        if cmd_result[0]!=0:
            if FileUtils.check_result(result[1]+result[2],['apt --fix-broken install -y']):
                if code==2: cmd_result = CmdTask("sudo apt install {} -y".format(dic_base[rosname]),300,os_command=False).run()
                elif code==1: cmd_result = CmdTask("sudo apt install ros-{}-desktop -y".format(rosname),300,os_command=False).run()
        # config env
        if cmd_result[0]==0:  
            # config_rosenv()
            run_tool_file('tools.tool_config_rosenv')
            PrintUtils.print_success("恭喜你，安装成功了，是不是很方便，打开fishros.com给小鱼来个一键三连吧~")
        else: PrintUtils.print_error("不好意思，安装失败了,请关注公众号鱼香ROS,反馈解决问题...")



    def run(self):
        self.install_ros()

