# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file



ros_mirror_dic = {
    "tsinghua":{"ROS1":"http://mirrors.tuna.tsinghua.edu.cn/ros/ubuntu/","ROS2":"http://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu/"},
    "huawei":{"ROS1":"https://repo.huaweicloud.com/ros/ubuntu/","ROS2":"https://repo.huaweicloud.com/ros2/ubuntu/"},
    "packages.ros":{"ROS1":"http://packages.ros.org/ros/ubuntu/","ROS2":"http://packages.ros.org/ros2/ubuntu/"},
    "repo-ros2":{"ROS2":"http://repo.ros2.org/ubuntu/"}
}


ros_dist_dic = {
    'artful':{"packages.ros"},
    'bionic':{"tsinghua","huawei","packages.ros"},
    'buster':{"packages.ros"},
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
    'buster':{"packages.ros"},
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


class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_CONFIG
        self.name = "?????????????????????"
        self.autor = '??????'


    def add_ros_source(self):
        """????????????ROS???"""
        dic = {1:"??????ROS/ROS2???",2:"?????????ROS/ROS2???"}
        code,result = ChooseTask(dic, "??????????????????ROS???ROS2??????").run()
        if code==2: return
        tool = run_tool_file('tools.tool_install_ros',autorun=False)
        if not tool.support_install(): return False
        # tool.check_sys_source()
        tool.add_key()
        tool.add_source()


    def change_sys_source(self):
        """
        ????????????
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
        debian = """
            deb https://mirrors.tuna.tsinghua.edu.cn/debian/ <code-name> main contrib non-free
            deb https://mirrors.tuna.tsinghua.edu.cn/debian/ <code-name>-updates main contrib non-free
            deb https://mirrors.tuna.tsinghua.edu.cn/debian/ <code-name>-backports main contrib non-free
            deb https://mirrors.tuna.tsinghua.edu.cn/debian-security <code-name>/updates main contrib non-free
        """


        PrintUtils.print_delay('?????????????????????????????????????????????[??????ROS]????????????..')
        # delete file
        dic = {1:"??????????????????",2:"????????????????????????????????????"}
        code,result = ChooseTask(dic, "?????????????????????,??????????????????????????????2").run()
        # ?????????????????????????????????
        # result = CmdTask('sudo apt update',100).run()

        FileUtils.delete('/etc/apt/sources.list')
        if code==2: 
            print("????????????????????????")
            FileUtils.delete('/etc/apt/sources.list.d')
            # fix add source failed before config system source 
            CmdTask('sudo mkdir -p /etc/apt/sources.list.d').run()
        
        # ?????????
        arch = AptUtils.getArch()
        PrintUtils.print_delay('??????????????????????????????[{}:{}],???????????????????????????..'.format(arch,osversion.get_codename()))
        source = normal
        if osversion.get_name().find("ubuntu")>=0:
            if arch=='amd64': source = normal
            else: source = ports
        elif osversion.get_name().find("debian")>=0:
            source = debian
        FileUtils.new('/etc/apt/','sources.list',source.replace("<code-name>",osversion.get_codename()))

        # update
        PrintUtils.print_delay("????????????????????????????????????....")
        result = CmdTask('sudo apt update',100).run()
        # https error update second
        if result[0]!= 0 and FileUtils.check_result(result[1]+result[2],['Certificate verification','??????']):
            PrintUtils.print_delay("??????????????????????????????????????????....")
            FileUtils.delete('/etc/apt/sources.list')
            FileUtils.new('/etc/apt/','sources.list',source.replace("https://","http://").replace("<code-name>",osversion.get_codename()))
            result = CmdTask('sudo apt update',100).run()
        if result[0]!=0:
            PrintUtils.print_info("??????????????????????????????????????????????????????...")
            result = CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 0E98404D386FA1D9",10).run()
            result = CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys DCC9EFBF77E11517",10).run()
            result = CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 54404762BBB6E853",10).run()
            result = CmdTask("apt-get install debian-keyring debian-archive-keyring",10).run()
            result = CmdTask("apt-key update",10).run()
            result = CmdTask('sudo apt update',100).run()
        if result[0]!=0:
            PrintUtils.print_info("""??????????????????NO_PUBKEY XXXXXXXX?????????????????????????????????apt-key adv --keyserver keyserver.ubuntu.com --recv-keys XXXXXXXX
??????error??? NO_PUBKEY 0E98404D386FA1D9
???????????????sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 0E98404D386FA1D9
            """)
        
        # final check
        if result[0]==0: 
            PrintUtils.print_success("?????????,????????????,????????????????????????????????????????????????~")
            PrintUtils.print_info(result[1])

        PrintUtils.print_success("??????????????????.....")

    def run(self):
        # ???????????????
        self.change_sys_source()
        # ?????? ROS Source
        self.add_ros_source()