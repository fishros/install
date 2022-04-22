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
        self.name = "一键更换系统源"
        self.autor = '小鱼'

    def get_mirror_by_code(self,code,arch='amd64'):
        """
        获取镜像通过系统版本号
        """
        ros1_choose_queue = ["tsinghua","huawei","packages.ros"]
        ros2_choose_queue = ["tsinghua","huawei","packages.ros"]
        
        # armhf架构，优先使用官方源
        if arch=='armhf': ros2_choose_queue =["packages.ros","tsinghua","huawei"]

        mirror = []
        for item in ros1_choose_queue:
            if item in ros_dist_dic[code]:
                mirror.append(ros_mirror_dic[item]['ROS1'])
                break
        for item in ros2_choose_queue:
            if item in ros2_dist_dic[code]:
                mirror.append(ros_mirror_dic[item]['ROS2'])
                break
        return mirror
        

    def add_key(self):
        # check apt
        if not AptUtils.checkapt(): return False
        # pre-install
        AptUtils.install_pkg('curl')
        AptUtils.install_pkg('gnupg2')

        # add key
        cmd_result = CmdTask("curl -s https://gitee.com/ohhuo/rosdistro/raw/master/ros.asc | sudo apt-key add -",10).run()
        if cmd_result[0]!=0:
            cmd_result = CmdTask("curl -s https://gitee.com/ohhuo/rosdistro/raw/master/ros.asc | sudo apt-key add -",10).run()
        if cmd_result[0]!=0:
            PrintUtils.print_info("导入密钥失败，开始更换导入方式并二次尝试...")
            cmd_result = CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F42ED6FBAB17C654",10).run()
        return cmd_result


    def add_source(self):
        """
        检查并添加ROS系统源
        """
        arch = AptUtils.getArch()
        if arch==None: return False
        #add source 
        mirrors = self.get_mirror_by_code(osversion.get_codename(),arch=arch)
        PrintUtils.print_info("根据您的系统，为您推荐安装源为{}".format(mirrors))
        source_data = ''
        for mirror in mirrors:
            source_data += 'deb [arch={}]  {} {} main\n'.format(arch,mirror,osversion.get_codename())
        FileUtils.delete('/etc/apt/sources.list.d/ros-fish.list')
        FileUtils.new('/etc/apt/sources.list.d/',"ros-fish.list",source_data)
        # update
        if not AptUtils.checkapt(): PrintUtils.print_error("换源后更新失败，请联系小鱼处理!") 


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
        debian = """
            deb https://mirrors.tuna.tsinghua.edu.cn/debian/ <code-name> main contrib non-free
            deb https://mirrors.tuna.tsinghua.edu.cn/debian/ <code-name>-updates main contrib non-free
            deb https://mirrors.tuna.tsinghua.edu.cn/debian/ <code-name>-backports main contrib non-free
            deb https://mirrors.tuna.tsinghua.edu.cn/debian-security <code-name>/updates main contrib non-free
        """


        PrintUtils.print_delay('欢迎使用一键换源工具，本工具由[鱼香ROS]小鱼贡献..')
        # delete file
        dic = {1:"仅更换系统源",2:"更换系统源并清理第三方源"}
        code,result = ChooseTask(dic, "请选择换源方式,如果不知道选什么请选2").run()
        # 尝试第一次更新索引文件
        # result = CmdTask('sudo apt update',100).run()

        FileUtils.delete('/etc/apt/sources.list')
        if code==2: 
            print("删除一个资源文件")
            FileUtils.delete('/etc/apt/sources.list.d')
        
        # 选择源
        arch = AptUtils.getArch()
        PrintUtils.print_delay('检测到当前系统架构为[{}],正在为你更换对应源..'.format(arch))
        source = normal
        if osversion.get_name().find("ubuntu")>=0:
            if arch=='amd64': source = normal
            else: source = ports
        elif osversion.get_name().find("debian")>=0:
            source = debian
        FileUtils.new('/etc/apt/','sources.list',source.replace("<code-name>",osversion.get_codename()))

        # update
        PrintUtils.print_delay("替换完成，尝试第一次更新....")
        result = CmdTask('sudo apt update',100).run()
        # https error update second
        if result[0]!= 0 and FileUtils.check_result(result[1]+result[2],['Certificate verification','证书']):
            PrintUtils.print_delay("发生证书错误，尝试第二次更新....")
            FileUtils.delete('/etc/apt/sources.list')
            FileUtils.new('/etc/apt/','sources.list',source.replace("https://","http://").replace("<code-name>",osversion.get_codename()))
            result = CmdTask('sudo apt update',100).run()
        if result[0]!=0:
            PrintUtils.print_info("更新失败，开始更换导入方式并三次尝试...")
            result = CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 0E98404D386FA1D9",10).run()
            result = CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys DCC9EFBF77E11517",10).run()
            result = CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 54404762BBB6E853",10).run()
            result = CmdTask("apt-get install debian-keyring debian-archive-keyring",10).run()
            result = CmdTask("apt-key update",10).run()
            result = CmdTask('sudo apt update',100).run()
        if result[0]!=0:
            PrintUtils.print_info("""如果出现问题NO_PUBKEY XXXXXXXX，请手动运行添加指令：apt-key adv --keyserver keyserver.ubuntu.com --recv-keys XXXXXXXX
如：error： NO_PUBKEY 0E98404D386FA1D9
运行指令：sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 0E98404D386FA1D9
            """)
        
        # final check
        if result[0]==0: 
            PrintUtils.print_success("搞定了,不信你看,累死宝宝了，还不快去给小鱼点个赞~")
            PrintUtils.print_info(result[1])
        PrintUtils.print_success("镜像修复完成.....")

    def run(self):
        #正式的运行
        self.change_source()