# -*- coding: utf-8 -*-
from pickle import NONE
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file


class RosVersion:
    STATUS_EOL = 0
    STATUS_LTS = 1
    def __init__(self,name,version,status,deps=[]):
        self.name = name
        self.version = version
        self.status = status
        self.deps = deps


class RosVersions:
    ros_version = [
        RosVersion('kinetic', 'ROS1', RosVersion.STATUS_EOL, ['python-catkin-tools','python-rosdep']),
        RosVersion('melodic', 'ROS1', RosVersion.STATUS_LTS, ['python-catkin-tools','python-rosdep']),
        RosVersion('noetic',  'ROS1', RosVersion.STATUS_LTS, ['python3-catkin-tools','python3-rosdep']),

        RosVersion('foxy',  'ROS2', RosVersion.STATUS_LTS, ['python3-colcon-common-extensions','python3-argcomplete','python3-rosdep']),
        RosVersion('galactic',  'ROS2', RosVersion.STATUS_LTS, ['python3-colcon-common-extensions','python3-argcomplete','python3-rosdep']),
        RosVersion('rolling',  'ROS2', RosVersion.STATUS_LTS, ['python3-colcon-common-extensions','python3-argcomplete','python3-rosdep']),
        RosVersion('humble',  'ROS2', RosVersion.STATUS_LTS, ['python3-colcon-common-extensions','python3-argcomplete','python3-rosdep']),
        RosVersion('eloquent',  'ROS2', RosVersion.STATUS_EOL, ['python3-colcon-common-extensions','python3-argcomplete','python3-rosdep']),
        RosVersion('dashing',  'ROS2', RosVersion.STATUS_EOL, []),
        RosVersion('crystal',  'ROS2', RosVersion.STATUS_EOL, []),
        RosVersion('bouncy',  'ROS2', RosVersion.STATUS_EOL, []),
        RosVersion('ardent',  'ROS2', RosVersion.STATUS_EOL, []),
        RosVersion('lunar', 'ROS2', RosVersion.STATUS_EOL, []),
    ]

    @staticmethod
    def get_version_string(name):
        for version in RosVersions.ros_version:
            if version.name == name:
                return "{}({})".format(version.name,version.version)

    @staticmethod
    def get_version(name):
        for version in RosVersions.ros_version:
            if version.name == name:
                return version
       
    @staticmethod
    def install_depend(name):
        depends = RosVersions.get_version(name).deps
        for dep in depends:
            AptUtils.install_pkg(dep)


    @staticmethod
    def tip_test_command(name):
        version = RosVersions.get_version(name).version
        if version=="ROS1":
            PrintUtils.print_warn("小鱼，黄黄的提示：您安装的是ROS1，可以打开一个新的终端输入roscore测试！")
        elif version=="ROS2":
            PrintUtils.print_warn("小鱼：黄黄的提示：您安装的是ROS2,ROS2是没有roscore的，请打开新终端输入ros2测试！小鱼制作了ROS2课程，关注公众号《鱼香ROS》即可获取~")

    @staticmethod
    def get_desktop_version(name):
        version = RosVersions.get_version(name).version
        if version=="ROS1":
            return "ros-{}-desktop-full".format(name)
        elif version=="ROS2":
            return "ros-{}-desktop".format(name)

ros_mirror_dic = {
    "tsinghua":{"ROS1":"http://mirrors.tuna.tsinghua.edu.cn/ros/ubuntu/","ROS2":"http://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu/"},
    "huawei":{"ROS1":"https://repo.huaweicloud.com/ros/ubuntu/","ROS2":"https://repo.huaweicloud.com/ros2/ubuntu/"},
    "packages.ros":{"ROS1":"http://packages.ros.org/ros/ubuntu/","ROS2":"http://packages.ros.org/ros2/ubuntu/"},
    "https.packages.ros":{"ROS1":"https://packages.ros.org/ros/ubuntu/","ROS2":"https://packages.ros.org/ros2/ubuntu/"},
    "repo-ros2":{"ROS2":"http://repo.ros2.org/ubuntu/"}
}


ros_dist_dic = {
    'artful':{"packages.ros"},
    'bionic':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'buster':{"packages.ros"},
    'cosmic':{"packages.ros"},
    'disco':{"packages.ros"},
    'eoan':{"packages.ros"},
    'focal':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'jessie':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'lucid':{"packages.ros"},
    'maverick':{"packages.ros"},
    'natty':{"packages.ros"},
    'oneiric':{"packages.ros"},
    'precise':{"packages.ros"},
    'quantal':{"packages.ros"},
    'raring':{"packages.ros"},
    'saucy':{"packages.ros"},
    'stretch':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'trusty':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'utopic':{"packages.ros"},
    'vivid':{"packages.ros"},
    'wheezy':{"packages.ros"},
    'wily':{"packages.ros"},
    'xenial':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'yakkety':{"packages.ros"},
    'zesty':{"packages.ros"},
}


ros2_dist_dic = {
    'bionic':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'bullseye':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'buster':{"packages.ros"},
    'cosmic':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'disco':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'eoan':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'focal':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'jessie':{"tsinghua","huawei"},
    'jammy':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'stretch':{"tsinghua","huawei","packages.ros","https.packages.ros"},
    'trusty':{"tsinghua","huawei"},
    'xenial':{"tsinghua","huawei","packages.ros","https.packages.ros"},
}



class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装ROS和ROS2,支持树莓派Jetson"
        self.type = BaseTool.TYPE_INSTALL
        self.autor = '小鱼'


    def get_mirror_by_code(self,code,arch='amd64',first_choose="tsinghua"):
        """
        获取镜像通过系统版本号
        """
        ros1_choose_queue = [first_choose,"tsinghua","huawei","packages.ros"]
        ros2_choose_queue = [first_choose,"tsinghua","huawei","packages.ros"]
        
        # armhf架构，优先使用官方源
        if arch=='armhf': ros2_choose_queue =["packages.ros","tsinghua","huawei"]

        mirror = []
        # 确认源里有对应的系统的，比如jammy
        if code in ros_dist_dic.keys():
            for item in ros1_choose_queue:
                if item in ros_dist_dic[code]:
                    mirror.append(ros_mirror_dic[item]['ROS1'])
                    break
         # 确认源里有对应的系统的，比如jammy
        if code in ros2_dist_dic.keys():
            for item in ros2_choose_queue:
                if item in ros2_dist_dic[code]:
                    mirror.append(ros_mirror_dic[item]['ROS2'])
                    break
        # if code in ['focal']:
        #     mirror.append(ros_mirror_dic['packages.ros']['ROS2'])
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
        if FileUtils.check_result(cmd_result,['trusted.gpg.d']):
            # curl -s https://gitee.com/ohhuo/rosdistro/raw/master/ros.asc | sudo gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/ros.gpg --import 
            # sudo chmod 644 /etc/apt/trusted.gpg.d/ros.gpg
            cmd_result = CmdTask("curl -s https://gitee.com/ohhuo/rosdistro/raw/master/ros.asc | sudo gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/ros.gpg --import",10).run()
            cmd_result = CmdTask("sudo chmod 644 /etc/apt/trusted.gpg.d/ros.gpg",10).run()
        return cmd_result


    def check_sys_source(self):
        # 更换系统源
        dic = {1:"更换系统源再继续安装",2:"不更换继续安装"}
        PrintUtils.print_warn("=========接下来这一步很重要，如果不知道怎么选请选择1========")
        code,result = ChooseTask(dic, "首次安装一定要换源并清理三方源，换源!!!系统默认国外源容易失败!!").run()
        if code==1: 
            tool = run_tool_file('tools.tool_config_system_source',autorun=False)
            tool.change_sys_source()

    def get_all_instsll_ros_pkgs(self):
        AptUtils.checkapt()
        dic_base = AptUtils.search_package('ros-base','ros-[A-Za-z]+-ros-base',"ros-","-base")
        if dic_base== None: return None
        ros_name = {}
        for a in dic_base.keys(): 
            ros_name[RosVersions.get_version_string(a)] = a
        if len(ros_name) == 0:
            return None
        return ros_name

    def add_source(self):
        """
        检查并添加ROS系统源
        """

        arch = AptUtils.getArch()
        if arch==None: return False

        #add source 1
        mirrors = self.get_mirror_by_code(osversion.get_codename(),arch=arch)
        PrintUtils.print_info("根据您的系统，为您推荐安装源为{}".format(mirrors))
        source_data = ''
        for mirror in mirrors:
            source_data += 'deb [arch={}]  {} {} main\n'.format(arch,mirror,osversion.get_codename())
        FileUtils.delete('/etc/apt/sources.list.d/ros-fish.list')
        FileUtils.new('/etc/apt/sources.list.d/',"ros-fish.list",source_data)

        ros_pkg = self.get_all_instsll_ros_pkgs()
        if ros_pkg and len(ros_pkg)>1:
            PrintUtils.print_success("恭喜，成功添加ROS源，接下来可以使用apt安装ROS或者使用[1]一键安装ROS安装！") 
            return
        
        #add source2 
        PrintUtils.print_warn("换源后更新失败，第二次开始切换源，尝试更换ROS2源为华为源！") 
        mirrors = self.get_mirror_by_code(osversion.get_codename(),arch=arch,first_choose="huawei")
        PrintUtils.print_info("根据您的系统，为您推荐安装源为{}".format(mirrors))
        source_data = ''
        for mirror in mirrors:
            source_data += 'deb [arch={}]  {} {} main\n'.format(arch,mirror,osversion.get_codename())
        FileUtils.delete('/etc/apt/sources.list.d/ros-fish.list')
        FileUtils.new('/etc/apt/sources.list.d/',"ros-fish.list",source_data)
        ros_pkg = self.get_all_instsll_ros_pkgs()
        if ros_pkg and len(ros_pkg)>1:
            PrintUtils.print_success("恭喜，成功添加ROS源，接下来可以使用apt安装ROS或者使用[1]一键安装ROS安装！") 
            return

        #add source2 
        PrintUtils.print_warn("换源后更新失败，第三次开始切换源，尝试更换ROS2源为ROS2官方源！") 
        mirrors = self.get_mirror_by_code(osversion.get_codename(),arch=arch,first_choose="packages.ros")
        PrintUtils.print_info("根据您的系统，为您推荐安装源为{}".format(mirrors))
        source_data = ''
        for mirror in mirrors:
            source_data += 'deb [arch={}]  {} {} main\n'.format(arch,mirror,osversion.get_codename())
        FileUtils.delete('/etc/apt/sources.list.d/ros-fish.list')
        FileUtils.new('/etc/apt/sources.list.d/',"ros-fish.list",source_data)
        ros_pkg = self.get_all_instsll_ros_pkgs()
        if ros_pkg and len(ros_pkg)>1:
            PrintUtils.print_success("恭喜，成功添加ROS源，接下来可以使用apt安装ROS或者使用[1]一键安装ROS安装！") 
            return

        PrintUtils.print_warn("换源后更新失败，第四次开始切换源，尝试使用https-ROS2官方源～！") 
        mirrors = self.get_mirror_by_code(osversion.get_codename(),arch=arch,first_choose="https.packages.ros")
        PrintUtils.print_info("根据您的系统，为您推荐安装源为{}".format(mirrors))
        source_data = ''
        for mirror in mirrors:
            source_data += 'deb [arch={}]  {} {} main\n'.format(arch,mirror,osversion.get_codename())
        FileUtils.delete('/etc/apt/sources.list.d/ros-fish.list')
        FileUtils.new('/etc/apt/sources.list.d/',"ros-fish.list",source_data)
        ros_pkg = self.get_all_instsll_ros_pkgs()
        if ros_pkg and len(ros_pkg)>1:
            PrintUtils.print_success("恭喜，成功添加ROS源，接下来可以使用apt安装ROS或者使用[1]一键安装ROS安装！") 
            return

        # echo >>/etc/apt/apt.conf.d/99verify-peer.conf "Acquire { https::Verify-Peer false }"
        if  not AptUtils.checkapt(): PrintUtils.print_error("四次换源后都失败了，请及时联系小鱼获取解决方案并处理！") 



    def support_install(self):
        # check support
        if (osversion.get_codename() not in ros_dist_dic.keys()) and (osversion.get_codename() not in ros2_dist_dic.keys()):
            PrintUtils.print_error("小鱼:检测当前系统{}{}:{} 暂不支持一键安装ROS,请关注公众号《鱼香ROS》获取帮助.".format(osversion.get_name(), osversion.get_version(),osversion.get_codename()))
            return False
        PrintUtils.print_success("小鱼:检测当前系统{}{}:{} 支持一键安装ROS".format(osversion.get_name(), osversion.get_version(),osversion.get_codename()))
        return True

    def install_success(self,name):
        """
        检查某个版本的ROS是否安装成功
        """
        result = CmdTask("ls /opt/ros/{}/setup.bash".format(name), 0).run()
        if str(result[1]).find('setup.bash') >= 1:
            return True
        return False

    

    def choose_and_install_ros(self):
        # search ros packages
        dic_base = AptUtils.search_package('ros-base','ros-[A-Za-z]+-ros-base',"ros-","-base")
        if dic_base== None: return False

        ros_name = {}
        for a in dic_base.keys(): 
            ros_name[RosVersions.get_version_string(a)] = a

        code,rosname = ChooseTask(ros_name.keys(),"请选择你要安装的ROS版本名称(请注意ROS1和ROS2区别):",True).run()
        if code==0: 
            PrintUtils.print_error("你选择退出。。。。")
            return
        version_dic = {1:rosname+"桌面版",2:rosname+"基础版(小)"}
        code,name = ChooseTask(version_dic,"请选择安装的具体版本(如果不知道怎么选,请选1桌面版):",False).run()
        
        if code==0: 
            print("你选择退出。。。。")
            return
        
        install_tool = 'aptitude'
        install_tool_apt = 'apt'
        if osversion.get_version() == "16.04":
            install_tool = 'apt'

        install_version = ros_name[rosname]

        if install_tool=='aptitude':
            AptUtils.install_pkg('aptitude')
            AptUtils.install_pkg('aptitude')

        # 先尝试使用apt 安装，之后再使用aptitude。
        if code==2:
            # 第一次尝试
            cmd_result = CmdTask("sudo {} install  {} -y".format(install_tool_apt,dic_base[install_version]),300,os_command=True).run()
            cmd_result = CmdTask("sudo {} install  {} -y".format(install_tool_apt,dic_base[install_version]),300,os_command=False).run()
            if FileUtils.check_result(cmd_result,['未满足的依赖关系','unmet dependencies','but it is not installable']):
                # 尝试使用aptitude解决依赖问题
                PrintUtils.print_warn("============================================================")
                PrintUtils.print_delay("请注意我，检测你在安装过程中出现依赖问题，请在稍后输入n,再选择y,即可解决")
                import time
                input("确认了解情况，请输入回车继续安装")
                cmd_result = CmdTask("sudo {} install   {} ".format(install_tool,install_version),300,os_command=True).run()
                cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool,dic_base[install_version]),300,os_command=False).run()
        
        elif code==1:
            cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool_apt,RosVersions.get_desktop_version(install_version)),300,os_command=True).run()
            cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool_apt,RosVersions.get_desktop_version(install_version)),300,os_command=False).run()
            if FileUtils.check_result(cmd_result,['未满足的依赖关系','unmet dependencies','but it is not installable']):
                # 尝试使用aptitude解决依赖问题
                PrintUtils.print_warn("============================================================")
                PrintUtils.print_delay("请注意我，检测你在安装过程中出现依赖问题，请在稍后输入n,再选择y,即可解决")
                import time
                input("确认了解情况，请输入回车继续安装")
                cmd_result = CmdTask("sudo {} install   {}".format(install_tool,RosVersions.get_desktop_version(install_version)),300,os_command=True).run()
                cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool,RosVersions.get_desktop_version(install_version)),300,os_command=False).run()

        # apt broken error
        if cmd_result[0]!=0:
            if FileUtils.check_result(cmd_result[1]+cmd_result[2],['apt --fix-broken install -y']):
                if code==2: cmd_result = CmdTask("sudo {} install   {} -y".formatinstall_tool,(dic_base[rosname]),300,os_command=False).run()
                elif code==1: cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool,rosname),300,os_command=False).run()

        # 安装额外的依赖
        RosVersions.install_depend(install_version)

        return install_version


    def config_env_and_tip(self,version_name):
        """
        配置系统源
        """
        if self.install_success(version_name):
            run_tool_file('tools.tool_config_rosenv')
            PrintUtils.print_success("恭喜你，安装成功了，再附赠你机器人学习宝藏网站：鱼香社区:https://fishros.org.cn/forum")
        else: PrintUtils.print_error("安装失败了,请打开鱼香社区：https://fishros.org.cn/forum 在一键安装专区反馈问题...")


    def install_ros(self):
        PrintUtils.print_delay('欢迎使用ROS开箱子工具，本工具由[鱼香ROS]小鱼贡献..')
        if not self.support_install(): return False

        self.check_sys_source()
        self.add_key()
        self.add_source()

        ros_version = self.choose_and_install_ros()
        self.config_env_and_tip(ros_version)
        if self.install_success(ros_version):
            RosVersions.tip_test_command(ros_version)


    def run(self):
        self.install_ros()

