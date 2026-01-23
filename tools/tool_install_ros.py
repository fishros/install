# -*- coding: utf-8 -*-
from pickle import NONE
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file
from .base import tr


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
        # ubuntu 24
        RosVersion('kilted',  'ROS2', RosVersion.STATUS_LTS, ['python3-colcon-core','python3-colcon-common-extensions','python3-argcomplete','python3-rosdep']),
        RosVersion('jazzy',  'ROS2', RosVersion.STATUS_LTS, ['python3-colcon-core','python3-colcon-common-extensions','python3-argcomplete','python3-rosdep']),
        # ubuntu 22 & 24
        RosVersion('rolling',  'ROS2', RosVersion.STATUS_LTS, ['python3-colcon-core','python3-colcon-common-extensions','python3-argcomplete','python3-rosdep']),
        RosVersion('eloquent',  'ROS2', RosVersion.STATUS_EOL, ['python3-colcon-core','python3-colcon-common-extensions','python3-argcomplete','python3-rosdep']),
        # ubuntu 22
        RosVersion('iron',  'ROS2', RosVersion.STATUS_LTS, ['python3-colcon-core','python3-colcon-common-extensions','python3-argcomplete','python3-rosdep']),
        RosVersion('humble',  'ROS2', RosVersion.STATUS_LTS, ['python3-colcon-core','python3-colcon-common-extensions','python3-argcomplete','python3-rosdep']),
        RosVersion('galactic',  'ROS2', RosVersion.STATUS_LTS, ['python3-colcon-core','python3-colcon-common-extensions','python3-argcomplete','python3-rosdep']),
        # ubuntu 20
        RosVersion('foxy',  'ROS2', RosVersion.STATUS_EOL, ['python3-colcon-core','python3-colcon-common-extensions','python3-argcomplete','python3-rosdep']),
        RosVersion('noetic',  'ROS1', RosVersion.STATUS_EOL, ['python3-catkin-tools','python3-rosdep']),
        # ubuntu 18
        RosVersion('melodic', 'ROS1', RosVersion.STATUS_LTS, ['python-catkin-tools','python-rosdep']),
        RosVersion('dashing',  'ROS2', RosVersion.STATUS_EOL, []),
        # ubuntu 16
        RosVersion('kinetic', 'ROS1', RosVersion.STATUS_EOL, ['python-catkin-tools','python-rosdep']),
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
        if depends:
            # 批量安装依赖包，提高效率
            dep_string = " ".join(depends)
            AptUtils.install_pkg(dep_string)

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


key_urls = [
    'https://gitee.com/fishros/rosdistro/raw/master/ros.asc',
    'https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc',
]

ros_mirror_dic = {
    "tsinghua":{"ROS1":"http://mirrors.tuna.tsinghua.edu.cn/ros/ubuntu/","ROS2":"http://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu/"},
    "mirrorz":{"ROS1":"http://mirrors.cernet.edu.cn/ros/ubuntu/","ROS2":"http://mirrors.cernet.edu.cn/ros2/ubuntu"},
    "ustc":{"ROS1":"https://mirrors.ustc.edu.cn/ros/ubuntu/","ROS2":"https://mirrors.ustc.edu.cn/ros2/ubuntu/"},
    "huawei":{"ROS1":"https://repo.huaweicloud.com/ros/ubuntu/","ROS2":"https://repo.huaweicloud.com/ros2/ubuntu/"},
    "packages.ros":{"ROS1":"http://packages.ros.org/ros/ubuntu/","ROS2":"http://packages.ros.org/ros2/ubuntu/"},
}


ros_dist_dic = {
    'artful': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'bionic': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'buster': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'cosmic': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'disco': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'eoan': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'focal': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'jessie': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'lucid': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'maverick': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'natty': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'oneiric': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'precise': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'quantal': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'raring': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'saucy': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'stretch': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'trusty': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'utopic': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'vivid': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'wheezy': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'wily': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'xenial': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'yakkety': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'zesty': {"tsinghua", "ustc", "huawei", "packages.ros", },
}


ros2_dist_dic = {
    'bionic': {"tsinghua", "mirrorz", "huawei", "packages.ros", },
    'bookworm': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'bullseye': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'buster': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'cosmic': {"packages.ros", },
    'disco': {"packages.ros", },
    'eoan': {"packages.ros", },
    'focal': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'jessie': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'jammy': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'noble': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'stretch': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'trixie': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'trusty': {"tsinghua", "ustc", "huawei", "packages.ros", },
    'xenial': {"tsinghua", "ustc", "huawei", "mirrorz", "packages.ros", },
    'utopic': {"packages.ros", },
    'yakkety': {"packages.ros", },
    'zesty': {"packages.ros", },
}

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装ROS和ROS2,支持树莓派Jetson"
        self.type = BaseTool.TYPE_INSTALL
        self.author = '小鱼'


    def get_mirror_by_code(self,code,arch='amd64',first_choose="tsinghua"):
        """
        获取镜像通过系统版本号
        """
        ros1_choose_queue = [first_choose,"tsinghua","ustc","huawei","packages.ros"]
        ros2_choose_queue = [first_choose,"tsinghua","ustc","huawei","packages.ros"]
        
        # armhf架构，优先使用官方源
        if arch=='armhf': ros2_choose_queue =["packages.ros","tsinghua","ustc","huawei"]

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

    def select_mirror(self):
        """
        让用户选择镜像源
        """
        # 检查当前系统是否支持中科大镜像
        codename = osversion.get_codename()
        supported_mirrors = []
        
        if codename in ros_dist_dic.keys() or codename in ros2_dist_dic.keys():
            if "ustc" in ros_dist_dic.get(codename, []) or "ustc" in ros2_dist_dic.get(codename, []):
                supported_mirrors.append("ustc")
                
        if codename in ros_dist_dic.keys() or codename in ros2_dist_dic.keys():
            if "tsinghua" in ros_dist_dic.get(codename, []) or "tsinghua" in ros2_dist_dic.get(codename, []):
                supported_mirrors.append("tsinghua")
                
        if codename in ros_dist_dic.keys() or codename in ros2_dist_dic.keys():
            if "huawei" in ros_dist_dic.get(codename, []) or "huawei" in ros2_dist_dic.get(codename, []):
                supported_mirrors.append("huawei")

        # 添加 mirrorz 镜像源支持
        if codename in ros_dist_dic.keys() or codename in ros2_dist_dic.keys():
            if "mirrorz" in ros_dist_dic.get(codename, []) or "mirrorz" in ros2_dist_dic.get(codename, []):
                supported_mirrors.append("mirrorz")

        # 如果系统支持多个镜像源，则让用户选择
        if len(supported_mirrors) > 1:
            mirror_dict = {}
            count = 1
            for mirror in supported_mirrors:
                if mirror == "ustc":
                    mirror_dict[count] = "中科大镜像源 (推荐国内用户使用)"
                elif mirror == "tsinghua":
                    mirror_dict[count] = "清华镜像源 (容易被封禁)"
                elif mirror == "huawei":
                    mirror_dict[count] = "华为镜像源"
                elif mirror == "mirrorz":
                    mirror_dict[count] = "中山大学开源软件镜像站 (试运行)"
                count += 1
            
            mirror_dict[count] = "ROS官方源 (国外用户或需要最新版本时使用)"
            
            code, result = ChooseTask(mirror_dict, "检测到您的系统支持多个ROS镜像源，请选择您想要使用的ROS镜像源(默认清华)：").run()
            if code == 0:
                return "tsinghua"  # 默认返回清华源
            elif code == count:
                return "packages.ros"  # 官方源
            else:
                # 根据选择返回对应的镜像源
                for key, value in mirror_dict.items():
                    if key == code:
                        if "中科大" in value:
                            return "ustc"
                        elif "清华" in value:
                            return "tsinghua"
                        elif "华为" in value:
                            return "huawei"
                        elif "中山大" in value:
                            return "mirrorz"
                    
                        
        else:
            # 系统只支持默认的清华源
            PrintUtils.print_info("您的系统默认使用清华镜像源")
            return "tsinghua"
        
        return "tsinghua"

    def add_source(self):
        """
        检查并添加ROS系统源
        """
        arch = AptUtils.getArch()
        if arch==None: return False

        # 让用户选择镜像源
        selected_mirror = self.select_mirror()
        PrintUtils.print_info("您选择的镜像源: {}".format(selected_mirror))

        #add source 1
        mirrors = self.get_mirror_by_code(osversion.get_codename(),arch=arch,first_choose=selected_mirror)
        PrintUtils.print_info("根据您的系统和选择，为您推荐安装源为{}".format(mirrors))
        source_data = ''
        for mirror in mirrors:
            source_data += 'deb [arch={}]  {} {} main\n'.format(arch,mirror,osversion.get_codename())
        FileUtils.delete('/etc/apt/sources.list.d/ros-fish.list')
        FileUtils.new('/etc/apt/sources.list.d/',"ros-fish.list",source_data)

        ros_pkg = self.get_all_instsll_ros_pkgs()
        if ros_pkg and len(ros_pkg)>1:
            PrintUtils.print_success("恭喜，成功添加ROS源，接下来可以使用apt安装ROS或者使用[1]一键安装ROS安装！") 
            return
        
        # 如果第一次尝试失败，让用户重新选择镜像源
        PrintUtils.print_warn("换源后更新失败，您可以重新选择镜像源再尝试！") 
        retry_mirror = self.select_mirror()
        while retry_mirror != selected_mirror:
            PrintUtils.print_info("您重新选择的镜像源: {}".format(retry_mirror))
            mirrors = self.get_mirror_by_code(osversion.get_codename(),arch=arch,first_choose=retry_mirror)
            PrintUtils.print_info("根据您的系统和选择，为您推荐安装源为{}".format(mirrors))
            source_data = ''
            for mirror in mirrors:
                source_data += 'deb [arch={}]  {} {} main\n'.format(arch,mirror,osversion.get_codename())
            FileUtils.delete('/etc/apt/sources.list.d/ros-fish.list')
            FileUtils.new('/etc/apt/sources.list.d/',"ros-fish.list",source_data)
            ros_pkg = self.get_all_instsll_ros_pkgs()
            if ros_pkg and len(ros_pkg)>1:
                PrintUtils.print_success("恭喜，成功添加ROS源，接下来可以使用apt安装ROS或者使用[1]一键安装ROS安装！") 
                return
            else:
                PrintUtils.print_warn("换源后更新失败，您可以重新选择镜像源再尝试！") 
                retry_mirror = self.select_mirror()
        else:
            PrintUtils.print_error("您选择了相同的镜像源，四次换源后都失败了，请及时联系小鱼获取解决方案并处理！")

    def add_key(self):
        PrintUtils.print_success(tr.tr('============正在添加ROS源密钥================='))
        # check apt
        if not AptUtils.checkapt(): 
            pass
        # install dep
        AptUtils.install_pkg('curl')
        AptUtils.install_pkg('gnupg2')

        # add key
        PrintUtils.print_success(tr.tr('正在挑选最快的密钥服务:{}').format(key_urls))
        key_url = AptUtils.get_fast_url(key_urls)
        if not key_url: 
            PrintUtils.print_error(tr.tr("获取密钥失败"))
            return
        key_url = key_url[0]
        PrintUtils.print_success(tr.tr('已自动选择最快密钥服务:{}').format(key_url))

        cmd_result = CmdTask("curl -s {} | sudo apt-key add -".format(key_url)).run()
        if cmd_result[0]!=0: 
            cmd_result = CmdTask("curl -s {} | sudo apt-key add -".format(key_url)).run()
        # 针对近期密钥更新问题
        CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F42ED6FBAB17C654",10).run()
        if cmd_result[0]!=0:
            PrintUtils.print_info(tr.tr("导入密钥失败，开始更换导入方式并二次尝试..."))
            cmd_result = CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F42ED6FBAB17C654",10).run()

        # 针对trusted.gpg.d问题解决方案
        if FileUtils.check_result(cmd_result,['trusted.gpg.d']):
            cmd_result = CmdTask("curl -s {} | sudo gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/ros.gpg --import".format(key_url)).run()
            cmd_result = CmdTask("sudo chmod 644 /etc/apt/trusted.gpg.d/ros.gpg",10).run()

        return cmd_result


    def check_sys_source(self):
        # 更换系统源
        dic = {1:"更换系统源再继续安装",2:"不更换继续安装"}
        PrintUtils.print_warn("=========接下来这一步很很很很重要，如果不知道怎么选请选择1========")
        code,result = ChooseTask(dic, "新手或首次安装一定要一定要一定要换源并清理三方源，换源!!!系统默认国外源容易失败!!").run()
        if code==1: 
            tool = run_tool_file('tools.tool_config_system_source',authorun=False)
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
            PrintUtils.print_error("你选择退出")
            PrintUtils.print_delay('是因为没有自己想要的ROS版本吗？ROS版本和操作系统版本是有对应关系的哦，所以可能是你的系统版本{}不对!具体请查看：https://fishros.org.cn/forum/topic/96'.format(str(str(osversion.get_name())+str(osversion.get_version()))))
            return False
        version_dic = {1:rosname+"桌面版",2:rosname+"基础版(小)"}
        code,name = ChooseTask(version_dic,"请选择安装的具体版本(如果不知道怎么选,请选1桌面版):",False).run()
        
        if code==0: 
            PrintUtils.print_error("你选择退出。。。。")
            return False
        
        install_tool = 'aptitude'
        install_tool_apt = 'apt'
        if osversion.get_version() == "16.04":
            install_tool = 'apt'

        install_version = ros_name[rosname]

        if install_tool=='aptitude':
            AptUtils.install_pkg('aptitude')

        # ======================================================基础版本==============================================================
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
                cmd_result = CmdTask("sudo {} install   {} ".format(install_tool,dic_base[install_version]),300,os_command=True).run()
                cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool,dic_base[install_version]),300,os_command=False).run()
        
        # ======================================================桌面版本==============================================================
        elif code==1:
            cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool_apt,RosVersions.get_desktop_version(install_version)),300,os_command=True).run()
            cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool_apt,RosVersions.get_desktop_version(install_version)),300,os_command=False).run()
            if FileUtils.check_result(cmd_result,['未满足的依赖关系','unmet dependencies','but it is not installable']):
                # 尝试使用aptitude解决依赖问题
                PrintUtils.print_warn("============================================================")
                PrintUtils.print_delay("请注意我，检测你在安装过程中出现依赖问题，请在稍后输入n,再选择y,即可解决（若无法解决，清在稍后手动运行命令: sudo aptitude install {})".format(RosVersions.get_desktop_version(install_version)))
                import time
                input("确认了解情况，请输入回车继续安装")
                cmd_result = CmdTask("sudo {} install   {}".format(install_tool,RosVersions.get_desktop_version(install_version)),300,os_command=True).run()
                cmd_result = CmdTask("sudo {} install   {} -y".format(install_tool,RosVersions.get_desktop_version(install_version)),300,os_command=False).run()

        # apt broken error
        if cmd_result[0]!=0:
            if FileUtils.check_result(cmd_result,['--fix-broken install']):
                CmdTask("sudo apt --fix-broken install -y").run()
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
        if not ros_version:
            return
        self.config_env_and_tip(ros_version)
        if self.install_success(ros_version):
            RosVersions.tip_test_command(ros_version)


    def run(self):
        self.install_ros()

