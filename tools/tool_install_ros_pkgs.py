# -*- coding: utf-8 -*-
import glob
import os
from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, AptUtils, ChooseTask, AdUtils
from .tool_install_ros import RosVersions

# ROS 桌面版不带导航、建图这些功能包, 新手装完 ROS 编译 FishBot 等机器人工作空间时最常缺的就是它们.
# 包名省略 ros-<版本>- 前缀; 安装前会逐个检查软件源里有没有, 没有的跳过(如 noetic 没有 cartographer-ros)
common_pkgs = {
    "ROS2": [
        ("导航 Nav2", ["navigation2", "nav2-bringup"]),
        ("建图 slam_toolbox", ["slam-toolbox"]),
        ("建图 Cartographer", ["cartographer-ros", "cartographer-rviz"]),
        ("键盘遥控", ["teleop-twist-keyboard"]),
        ("手柄遥控(USB 接收器/有线手柄)", ["joy", "teleop-twist-joy"]),
        ("机器人模型 xacro / 关节调试界面", ["xacro", "joint-state-publisher-gui"]),
        ("多传感器融合定位", ["robot-localization"]),
    ],
    "ROS1": [
        ("导航 navigation", ["navigation"]),
        ("建图 gmapping", ["slam-gmapping"]),
        ("建图 Cartographer", ["cartographer-ros"]),
        ("键盘遥控", ["teleop-twist-keyboard"]),
        ("手柄遥控(USB 接收器/有线手柄)", ["joy", "teleop-twist-joy"]),
        ("机器人模型 xacro / 关节调试界面", ["xacro", "joint-state-publisher-gui"]),
        ("多传感器融合定位", ["robot-localization"]),
    ],
}
# 与 ROS 版本无关的系统包: 串口通信, 机器人底盘驱动常用
system_pkgs = [
    ("串口通信 pyserial", ["python3-serial"]),
    ("手柄测试工具 jstest", ["joystick"]),
]


class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装ROS常用功能包(导航/建图)"
        self.type = BaseTool.TYPE_INSTALL
        self.author = "小鱼"

    @staticmethod
    def installed_ros():
        return sorted(
            os.path.basename(os.path.dirname(path)) for path in glob.glob("/opt/ros/*/setup.bash")
        )

    @staticmethod
    def in_apt_index(pkg):
        return CmdTask("apt-cache show {} > /dev/null 2>&1".format(pkg), 10).run()[0] == 0

    def plan(self, version):
        """返回 [(说明, [可装的完整包名])], 软件源里没有的包跳过"""
        info = RosVersions.get_version(version)
        ros_type = info.version if info else "ROS2"
        groups = [
            (label, ["ros-{}-{}".format(version, p) for p in pkgs])
            for label, pkgs in common_pkgs.get(ros_type, common_pkgs["ROS2"])
        ] + system_pkgs
        result = []
        for label, pkgs in groups:
            available = [p for p in pkgs if self.in_apt_index(p)]
            if available:
                result.append((label, available))
            else:
                PrintUtils.print_info("软件源里没有 {}, 跳过".format(label))
        return result

    def install_common(self, version, auto=False):
        """
        为指定 ROS 版本安装常用功能包. auto=True 时不再询问(全自动模式调用)
        返回是否全部安装成功
        """
        AptUtils.wait_and_repair()
        AptUtils.checkapt()
        groups = self.plan(version)
        if not groups:
            PrintUtils.print_error("软件源里找不到 {} 的功能包, 请先用一键安装 [1] 添加 ROS 软件源".format(version))
            return False
        PrintUtils.print_success("将为 {} 安装以下常用功能包:".format(RosVersions.get_version_string(version) or version))
        for label, pkgs in groups:
            PrintUtils.print_info("  - {}: {}".format(label, " ".join(pkgs)))
        if not auto:
            code, _ = ChooseTask({1: "安装以上全部(额外下载几百MB)"}, "请确认:").run()
            if code != 1:
                return False

        pkgs = [p for _, group in groups for p in group]
        cmd = "sudo apt install -y {}".format(" ".join(pkgs))
        result = CmdTask(cmd, 0).run()
        if result[0] != 0 and FileUtils.check_result(result, ["Unable to fetch", "--fix-missing", "无法下载"]):
            PrintUtils.print_warn("部分软件包下载失败, 刷新软件源后重试一次...")
            CmdTask("sudo apt update", 100).run()
            CmdTask("sudo apt install -y --fix-missing {}".format(" ".join(pkgs)), 0).run()

        failed = [p for p in pkgs if CmdTask("dpkg -s {} > /dev/null 2>&1".format(p), 10).run()[0] != 0]
        if failed:
            PrintUtils.print_error("以下功能包没有装上: {}".format(" ".join(failed)))
            PrintUtils.print_info("可以稍后手动重试: sudo apt install -y {}".format(" ".join(failed)))
            return False
        PrintUtils.print_success("常用功能包已全部装好, 新开终端即可使用")
        self.print_joy_tips(version)
        return True

    @staticmethod
    def print_joy_tips(version):
        info = RosVersions.get_version(version)
        ros1 = info is not None and info.version == "ROS1"
        PrintUtils.print_info("手柄怎么用: 插上 USB 接收器(虚拟机要在 VMware 菜单「虚拟机 > 可移动设备」里把它连到虚拟机)")
        PrintUtils.print_info("  1. 测试手柄是否被识别: jstest /dev/input/js0   (按键/摇杆时数字会变化)")
        if ros1:
            PrintUtils.print_info("  2. 读取手柄数据: rosrun joy joy_node, 另开终端 rostopic echo /joy")
            PrintUtils.print_info("  3. 手柄控制机器人: roslaunch teleop_twist_joy teleop.launch joy_config:=xbox")
        else:
            PrintUtils.print_info("  2. 读取手柄数据: ros2 run joy joy_node, 另开终端 ros2 topic echo /joy")
            PrintUtils.print_info("  3. 手柄控制机器人: ros2 launch teleop_twist_joy teleop-launch.py joy_config:=xbox")
        PrintUtils.print_info("     (teleop_twist_joy 默认要按住使能键才会发速度, 不同手柄键位可换 joy_config:=ps3 等)")

    def run(self):
        versions = self.installed_ros()
        if not versions:
            PrintUtils.print_error("当前系统还没有安装ROS, 请先使用一键安装 [1] 安装ROS")
            return False
        version = versions[0]
        if len(versions) > 1:
            code, version = ChooseTask(versions, "检测到安装了多个ROS, 请选择要给哪个版本安装功能包:", True).run()
            if code == 0:
                return False
        if not self.install_common(version):
            AdUtils.mark_failed()
            return False
        AdUtils.show("pkgs_installed")
