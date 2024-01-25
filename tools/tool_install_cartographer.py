# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file
import os

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装Cartographer"
        self.type = BaseTool.TYPE_INSTALL
        self.autor = 'catalpa'

    def get_sys_default_ros_version(self):
        if osversion.get_version().find('18')>=0:
            return 'melodic'
        if osversion.get_version().find('20')>=0:
            return 'noetic'
        if osversion.get_version().find('16')>=0:
            return 'kinetic'

    def install_docker(self):
        ros_version = self.get_sys_default_ros_version()

        PrintUtils.print_info("欢迎使用一键编译安装Cartographer，该工具将会以当前目录作为工作区，创建src文件夹并进行cartographer的编译安装")
        PrintUtils.print_info("使用一键安装前，若未安装ROS或出现错误，可以使用一键安装ROS")

        if ros_version!=None:
            PrintUtils.print_info("检测到您的系统版ROS版本为：{}".format(ros_version))
        else:
            PrintUtils.print_info("检测系统版本失败，请反馈以下信息到鱼香社区：Fail on check ros version with {}".format(osversion.get_version()))
            return

        # check apt
        if not AptUtils.checkapt(): return False
        # 1
        CmdTask('sudo apt install ninja-build stow git -y').run()
        # 2
        CmdTask('mkdir -p cartographer_ws/src').run()
        CmdTask('git clone https://gitee.com/yuzi99url/cartographer_ros.git',path='cartographer_ws/src').run()
        CmdTask('git clone https://gitee.com/yuzi99url/cartographer.git',path='cartographer_ws/src').run()
        # 3
        CmdTask("sudo apt-get install libamd2 libatlas3-base libbtf1 libcamd2 libccolamd2 libceres-dev libceres1 libcholmod3 libcxsparse3 libgflags-dev libgflags2.2 libgoogle-glog-dev libgoogle-glog0v5 libklu1 libldl2 liblua5.2-0 liblua5.2-dev libmetis5 libncurses5 libncursesw5 librbio2 libreadline-dev libspqr2 libsuitesparse-dev libtinfo-dev libtinfo5 libtool-bin libumfpack5 -y").run()
        if ros_version == "melodic":
            CmdTask('sudo apt-get libgraphblas1 -y').run()
        # 4
        CmdTask("sudo apt-get remove ros-{}-abseil-cpp -y".format(ros_version)).run()
        FileUtils.find_replace("cartographer_ws/src/cartographer/scripts/install_abseil.sh", "https://github.com/abseil/abseil-cpp.git", "https://gitee.com/yuzi99url/abseil-cpp.git")
        CmdTask('bash src/cartographer/scripts/install_abseil.sh',path='cartographer_ws').run()
        # 5
        CmdTask("catkin_make_isolated --install --use-ninja",'cartographer_ws').run()
        CmdTask("sudo chmod -R 777 cartographer_ws").run()

    def run(self):
        self.install_docker()

