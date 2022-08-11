# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file

class RosVersion:
    STATUS_EOL = 0
    STATUS_LTS = 1
    def __init__(self,name,version,status,images=[],arm_images=[]):
        self.name = name
        self.version = version
        self.status = status
        self.images = images
        self.arm_images = arm_images


class RosVersions:
    ros_version = [
        RosVersion('noetic',  'ROS1', RosVersion.STATUS_LTS, ['fishros2/ros:noetic-desktop-full'],["ros:noetic"]),
        RosVersion('humble',  'ROS2', RosVersion.STATUS_LTS, ['fishros2/ros:humble-desktop-full'],["ros:humble"]),
        RosVersion('foxy',  'ROS2', RosVersion.STATUS_LTS, ['fishros2/ros:foxy-desktop'],["ros:foxy"]),
        RosVersion('galactic',  'ROS2', RosVersion.STATUS_LTS, ['osrf/ros:galactic-desktop'],["ros:galactic"]),
        RosVersion('melodic', 'ROS1', RosVersion.STATUS_LTS, ['fishros2/ros:melodic-desktop-full'],["ros:melodic"]),
        RosVersion('rolling',  'ROS2', RosVersion.STATUS_LTS, ['osrf/ros:rolling-desktop-full'],["ros:rolling"]),
        RosVersion('kinetic', 'ROS1', RosVersion.STATUS_EOL, ['osrf/ros:kinetic-desktop-full'],["ros:kinetic"]),
        RosVersion('eloquent',  'ROS2', RosVersion.STATUS_EOL, ['osrf/ros:eloquent-desktop'],["ros:eloquent"]),
        RosVersion('dashing',  'ROS2', RosVersion.STATUS_EOL, ['osrf/ros:dashing-desktop'],["ros:dashing"]),
        RosVersion('crystal',  'ROS2', RosVersion.STATUS_EOL, ['osrf/ros:crystal-desktop'],["ros:crystal"]),
        RosVersion('bouncy',  'ROS2', RosVersion.STATUS_EOL, ['osrf/ros:bouncy-desktop'],["ros:bouncy"]),
        RosVersion('ardent',  'ROS2', RosVersion.STATUS_EOL, ['osrf/ros:ardent-desktop'],["ros:ardent"]),
        RosVersion('lunar', 'ROS2', RosVersion.STATUS_EOL, ['osrf/ros:lunar-desktop'],["ros:lunar"]),
        RosVersion('indigo', 'ROS1', RosVersion.STATUS_EOL, ['osrf/ros:indigo-desktop-full'],["ros:indigo"])
    ]

    @staticmethod
    def get_version_string(name):
        for version in RosVersions.ros_version:
            if version.name == name:
                if version.status==RosVersion.STATUS_EOL:
                    eol = "停止维护"
                else:
                    eol = "长期支持"
                return "{}({}),该版本目前状态:{}".format(version.name,version.version,eol)

    @staticmethod
    def get_image(name):
        for version in RosVersions.ros_version:
            if version.name == name:
                if osarch=="arm64":
                    return version.arm_images[0]
                return version.images[0]

    @staticmethod
    def get_ros_version(name):
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
    def get_vesion_list():
        """获取可安装的ROS版本列表"""
        names = []
        for version in RosVersions.ros_version:
            names.append(version.name)
        return names


class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装ROS-Docker版,支持所有版本ROS"
        self.type = BaseTool.TYPE_INSTALL
        self.autor = '小鱼'

    def get_container_scripts(self, name, rosversion, delete_file):
        delete_command = "sudo rm -rf {}".format(delete_file)
        ros1 = """xhost +local: >> /dev/null
echo "请输入指令控制{}: 重启(r) 进入(e) 启动(s) 关闭(c) 删除(d) 测试(t):"
read choose
case $choose in
s) docker start {};;
r) docker restart {};;
e) docker exec -it {} /bin/bash;;
c) docker stop {};;
d) docker stop {} && docker rm {} && {};;
t) docker exec -it {}  /bin/bash -c "source /ros_entrypoint.sh && roscore";;
esac
newgrp docker
""".format(name,name,name,name,name,name,name,delete_command,name)
        ros2 = """xhost +local: >> /dev/null
echo "请输入指令控制{}: 重启(r) 进入(e) 启动(s) 关闭(c) 删除(d) 测试(t):"
read choose
case $choose in
s) docker start {};;
r) docker restart {};;
e) docker exec -it {} /bin/bash;;
c) docker stop {};;
d) docker stop {} && docker rm {} && {};;
t) docker exec -it {}  /bin/bash -c "source /ros_entrypoint.sh && ros2";;
esac
newgrp docker
""".format(name,name,name,name,name,name,name,delete_command,name)
        if rosversion=="ROS1":
            return ros1
        return ros2

    def choose_image_version(self):
        """获取要安装的ROS版本"""
        PrintUtils.print_success("================================1.版本选择======================================")
        code,rosname = ChooseTask(RosVersions.get_vesion_list(),"请选择你要安装的ROS版本名称(请注意ROS1和ROS2区别):",True).run()
        if code==0: 
            PrintUtils.print_error("你选择退出。。。。")
            return 
        PrintUtils.print_info("你选择了{}".format(RosVersions.get_version_string(rosname)))
        return rosname
        # TODO 检查是系统架构

    def install_docker(self):
        """安装Docker"""
        PrintUtils.print_success("================================2.安装Docker======================================")
        result = CmdTask("docker version").run()
        if(result[0]==0): return
        run_tool_file('tools.tool_install_docker')
        # TODO 检查是否安装成功

    def download_image(self,name):
        """"""
        PrintUtils.print_success("=================3.下载镜像（该步骤因网络原因会慢一些，若失败请重试）==================")
        CmdTask('sudo docker pull {} '.format(RosVersions.get_image(name)),os_command=True).run()
        CmdTask('sudo docker pull {} '.format(RosVersions.get_image(name)),os_command=True).run()
        CmdTask('sudo docker pull {} '.format(RosVersions.get_image(name)),os_command=True).run()

        # create image
        # TODO 更换好系统源
        # FROM xxx
        # COPY 源
        # update && install wget
        # 一鍵還原添加ROS

    def create_container(self,name):
        """创建容器"""
        PrintUtils.print_success("================================4.生成容器======================================")
        # get a name
        PrintUtils.print_warn("请为你的{}容器取个名字吧！".format(name))
        container_name = input(">>")
        PrintUtils.print_info("收到名字{}".format(container_name))
        # get home
        user =  FileUtils.getusers()[0]
        home = "/home/{}".format(user)

        if container_name:
            command_create_x11 = "sudo docker run -dit --name={} -v {}:{} -v /tmp/.X11-unix:/tmp/.X11-unix --device=/dev/dri/renderD128 -v /dev/dri:/dev/dri --device /dev/snd -e DISPLAY=unix$DISPLAY -w {}  {}".format(
                    container_name,home,home,home,RosVersions.get_image(name))
        else:
            command_create_x11 = "sudo docker run -dit  -v {}:{} -v /tmp/.X11-unix:/tmp/.X11-unix --device=/dev/dri/renderD128 -v /dev/dri:/dev/dri --device /dev/snd -e DISPLAY=unix$DISPLAY -w {}  {}".format(
                    home,home,home,RosVersions.get_image(name))

        CmdTask(command_create_x11,os_command=True).run()
        # CmdTask("""docker exec -it {} /bin/bash -c "echo -e '\nsource /ros_entrypoint.sh' >> ~/.bashrc" """.format(container_name),os_command=True).run()
        CmdTask("""docker exec -it {} /bin/bash -c "echo -e '\nsource /opt/ros/{}/setup.bash' >> ~/.bashrc" """.format(container_name,name),os_command=True).run()
        # docker exec -it noetic-test1  /bin/bash -c "source /opt/ros/noetic/setup.bash  && roscore"
        # test command
        CmdTask("xhost +local:",os_command=True).run()
        return container_name


    def generte_command(self,container_name,rosname):
        """生成命令"""
        PrintUtils.print_success("================================5.生成命令======================================")
        rosversion = RosVersions.get_ros_version(rosname).version
        user =  FileUtils.getusers()[0]
        bashrc = '/home/{}/.bashrc'.format(user)
        bin_path = "/home/{}/.fishros/bin/".format(user)
        home = "/home/{}".format(user)

        # create file
        FileUtils.new(bin_path,container_name,self.get_container_scripts(container_name,rosversion,bin_path+container_name))
        FileUtils.find_replace_sub(bashrc,"# >>> fishros scripts >>>","# <<< fishros scripts <<<", "")
        FileUtils.append(bashrc,'# >>> fishros scripts >>>\nexport PATH=$PATH:{} \n# <<< fishros scripts <<<'.format(bin_path))
        CmdTask('sudo chmod 777 {}'.format(bin_path+container_name),os_command=True).run()


    def install_use_tool(self):
        """安装后续使用工具"""
        PrintUtils.print_success("================================6.生成使用工具======================================")
        tool_dic = {1:"套餐1:VsCode+插件（本地使用推荐）",2:"套餐2:SSH-Service（远程使用推荐）"}
        code,name = ChooseTask(tool_dic,"为方便后续使用容器，请选择使用方式，若不知道怎么选，推荐套餐1,若不需要则可以选退出:",False).run()
        if code==1:
            PrintUtils.print_info("套餐1包含Vscode及其容器插件，开始安装。。")
            run_tool_file('tools.tool_install_vscode')
            CmdTask('code --install-extension ms-vscode-remote.remote-containers --user-data-dir',os_command=True).run()
        elif code==2:
            CmdTask('sudo apt update',os_command=True).run()
            CmdTask('sudo apt install openssh-server -y',os_command=True).run()
            CmdTask('service ssh start',os_command=True).run()
        return 


    def install_ros_with_docker(self):
        rosname = self.choose_image_version()
        if not rosname: return

        self.install_docker()
        self.download_image(rosname)
        container_name = self.create_container(rosname)
        self.generte_command(container_name,rosname)
        self.install_use_tool()

        PrintUtils.print_success("===========================后续使用指令=================================")
        PrintUtils.print_info("后续可在任意终端输入{}来启动/停止/测试/删除容器".format(container_name))
        PrintUtils.print_success("==============================文件存储位置===============================")
        PrintUtils.print_info("你的主目录已经和容器的对应目录做了映射")
        PrintUtils.print_warn("==============================问题反馈&&更新讨论=============================")
        PrintUtils.print_info("请访问社区的一键安装版块：https://fishros.org.cn/forum/topic/112")

    def run(self):
        self.install_ros_with_docker()
