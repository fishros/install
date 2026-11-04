# -*- coding: utf-8 -*-
import os
import shutil
from urllib.parse import urlparse
from .base import BaseTool
from .base import PrintUtils, AptUtils, ChooseTask, AdUtils, StatUtils
from .base import osversion
from .base import run_tool_file
from .tool_install_ros import RosVersions

# 每个系统推荐给新手的 ROS 版本(按优先级). 统一推荐该系统对应的 ROS2 长期支持版,
# 18.04 上的 ROS2 早已停止维护且国内镜像不全, 推荐 ROS1 melodic
recommend_ros = {
    "bionic": ["melodic"],
    "focal": ["foxy", "noetic"],
    "jammy": ["humble"],
    "noble": ["jazzy"],
    "resolute": ["lyrical"],
}
# 推荐表里没有的系统(如 Debian), 按这个顺序挑第一个能装的
fallback_ros = ["lyrical", "jazzy", "humble", "foxy", "kilted", "iron", "galactic", "noetic", "melodic", "rolling"]

# 桌面版装完约占 3~4GB, 剩余空间不足时自动改装基础版
min_free_gb_for_desktop = 6
min_free_gb = 2


class Tool(BaseTool):
    def __init__(self):
        self.name = "全自动安装ROS(新手推荐)"
        self.type = BaseTool.TYPE_INSTALL
        self.author = "小鱼"

    @staticmethod
    def pick_version(codename, available):
        for name in recommend_ros.get(codename, []) + fallback_ros:
            if name in available:
                return name
        return sorted(available)[0] if available else None

    @staticmethod
    def free_gb():
        try:
            return shutil.disk_usage("/").free / 1024.0 / 1024 / 1024
        except Exception:
            return 100

    def system_mirror_failed(self, source_tool):
        """最后一次安装的报错里是否有当前系统镜像的下载失败"""
        source = getattr(source_tool, "current_source", None)
        result = getattr(self.ros_tool, "last_install_result", None)
        if not source or not result or len(result) < 3:
            return False
        host = urlparse(source).netloc
        output = " ".join(str(line) for line in list(result[1]) + list(result[2]))
        return host in output and ("Failed to fetch" in output or "无法下载" in output)

    def show_plan(self, expect_version, desktop):
        ros_name = "适合本系统的ROS版本(添加软件源后自动确定)"
        if expect_version:
            info = RosVersions.get_version_string(expect_version)
            ros_name = "{} {}".format(info, "桌面版" if desktop else "基础版")
        PrintUtils.print_success("=" * 60)
        PrintUtils.print_success(
            "检测到您的系统: {} {} ({}), 架构 {}".format(
                osversion.get_name().capitalize(),
                osversion.get_version(),
                osversion.get_codename(),
                AptUtils.getArch(),
            )
        )
        PrintUtils.print_info("全自动模式将依次完成以下步骤, 中途不需要再做选择:")
        PrintUtils.print_info("  1. 更换系统软件源: 自动测速, 选最快的镜像(原配置会备份)")
        PrintUtils.print_info("  2. 添加ROS软件源: 自动测速选镜像, 遇到坏掉的镜像自动换下一个")
        PrintUtils.print_info("  3. 安装 {}".format(ros_name))
        PrintUtils.print_info("  4. 配置环境变量, 新开终端就能直接使用ROS; 工作空间放在中文路径(如 ~/桌面)下也能编译")
        if desktop:
            PrintUtils.print_info("预计下载 0.5~1GB, 占用磁盘 3~4GB, 用时 10~40 分钟(取决于网速)")
        PrintUtils.print_success("=" * 60)

    def print_next_steps(self, version, desktop):
        ros1 = RosVersions.get_version(version).version == "ROS1"
        PrintUtils.print_success("接下来这样验证ROS是否装好(请先新开一个终端):")
        if ros1:
            PrintUtils.print_info("  终端1输入: roscore")
            if desktop:
                PrintUtils.print_info("  终端2输入: rosrun turtlesim turtlesim_node      (会弹出一只小乌龟)")
                PrintUtils.print_info("  终端3输入: rosrun turtlesim turtle_teleop_key   (在这个终端按方向键控制小乌龟)")
        elif desktop:
            PrintUtils.print_info("  终端1输入: ros2 run turtlesim turtlesim_node      (会弹出一只小乌龟)")
            PrintUtils.print_info("  终端2输入: ros2 run turtlesim turtle_teleop_key   (在这个终端按方向键控制小乌龟)")
        else:
            PrintUtils.print_info("  输入: ros2 topic list   (能列出 /rosout 等话题就说明正常)")

    def run(self):
        self.ros_tool = run_tool_file("tools.tool_install_ros", authorun=False)
        if not self.ros_tool.support_install():
            return False

        free = self.free_gb()
        if free < min_free_gb:
            PrintUtils.print_error("磁盘剩余空间只有 {:.1f}GB, 不够安装ROS, 请先清理磁盘或给虚拟机扩容".format(free))
            return False
        desktop = free >= min_free_gb_for_desktop
        if not desktop:
            PrintUtils.print_warn("磁盘剩余空间 {:.1f}GB, 不够装桌面版, 将改为安装基础版(无图形工具)".format(free))

        codename = osversion.get_codename()
        expect = recommend_ros.get(codename, [None])[0]
        while True:
            self.show_plan(expect, desktop)
            code, _ = ChooseTask(
                {
                    1: "开始全自动安装(推荐)",
                    2: "我要自己选(进入高手自定义模式)",
                },
                "请确认:",
            ).run()
            if code == 0:
                return BaseTool.BACK
            if code == 1:
                break
            # 高手模式第一步选了返回上一步, 回到这个确认界面
            result = self.ros_tool.install_ros()
            if result != BaseTool.BACK:
                return result

        # 统计: 确认开始算一次「开始安装」, 之后中途报错退出和装完检测不到都记失败
        StatUtils.report("ros:novice:start")
        # 之前跑过一半(自定义模式选到一半退出、Ctrl+C 打断)留下的 apt 锁/未配置完的包先处理掉
        AptUtils.wait_and_repair()
        source_tool = run_tool_file("tools.tool_config_system_source", authorun=False)
        source_tool.change_sys_source(auto=True)

        self.ros_tool.add_key()
        if not self.ros_tool.add_source(auto=True):
            StatUtils.report_ros_result("novice", False)
            return False

        dic_base = AptUtils.search_package("ros-base", "ros-[A-Za-z]+-ros-base", "ros-", "-base")
        if not dic_base:
            PrintUtils.print_error("软件源里没有找到可安装的ROS, 请携带 /tmp/fishros_install.log 到鱼香社区反馈")
            StatUtils.report_ros_result("novice", False)
            return False
        version = self.pick_version(codename, list(dic_base.keys()))
        if expect and version != expect:
            PrintUtils.print_warn("推荐的 {} 当前无法安装, 改为安装 {}".format(expect, version))
        PrintUtils.print_success(
            "开始安装 {} {}, 请耐心等待...".format(
                RosVersions.get_version_string(version), "桌面版" if desktop else "基础版"
            )
        )

        install_code = 1 if desktop else 2
        self.ros_tool.install_ros_packages(version, install_code, dic_base)
        for retry in range(2):
            if self.ros_tool.install_success(version) or not self.system_mirror_failed(source_tool):
                break
            new_source = source_tool.switch_to_next_source()
            if not new_source:
                break
            PrintUtils.print_warn("系统镜像下载中途失败, 已自动换用 {} 继续安装(已下载的包不会重复下载)".format(new_source))
            self.ros_tool.install_ros_packages(version, install_code, dic_base)
        self.ros_tool.config_env_and_tip(version)
        StatUtils.report_ros_result("novice", self.ros_tool.install_success(version))
        if self.ros_tool.install_success(version):
            self.print_next_steps(version, desktop)
        self.print_summary(source_tool, expect, version, desktop)
        if self.ros_tool.install_success(version):
            AdUtils.show("ros_installed")
        return True

    def print_summary(self, source_tool, expect, version, desktop):
        """小白模式装完后列出帮用户选了什么; 没装成功时也列出来, 方便反馈问题时对照排查"""
        ok = self.ros_tool.install_success(version)
        PrintUtils.print_success("=" * 60)
        if ok:
            PrintUtils.print_success("安装完成! 小白模式帮你做了这些选择:")
        else:
            PrintUtils.print_warn("安装没有成功, 本次自动做的选择如下, 到社区反馈问题时请一起贴上:")

        source = getattr(source_tool, "current_source", None)
        if source:
            backups = [b for b, original in source_tool.backups if original == "/etc/apt/sources.list"]
            if source_tool.use_deb822:
                backups.append("/etc/apt/ubuntu.sources.fishros.bak")
            PrintUtils.print_info("  系统软件源: {} {} (测速最快)".format(source_tool.source_names.get(source, ""), source))
            if backups:
                PrintUtils.print_info("              原来的配置已备份到 {}".format(backups[0]))
        else:
            PrintUtils.print_info("  系统软件源: 自动更换失败, 保留了原来的系统源")

        mirrors = getattr(self.ros_tool, "ros_mirrors", None)
        PrintUtils.print_info("  ROS软件源:  {} (测速最快, 且确认包能下载)".format(", ".join(mirrors) if mirrors else "添加失败"))
        key = getattr(self.ros_tool, "key_source", None)
        PrintUtils.print_info("  ROS公钥:    {}".format("来自 {}, 已核对官方指纹".format(key) if key else "已通过备用方式导入"))

        reason = "{} {} 对应的推荐版本".format(osversion.get_name().capitalize(), osversion.get_version())
        if expect and version != expect:
            reason = "推荐的 {} 当前无法安装, 改装了它".format(expect)
        kind = "桌面版(带小乌龟、RViz 等图形工具)" if desktop else "基础版(磁盘剩余不足 {}GB, 没装图形工具)".format(min_free_gb_for_desktop)
        PrintUtils.print_info("  ROS版本:    {} {}, {}".format(RosVersions.get_version_string(version), kind, reason))

        PrintUtils.print_info("  常用功能包: 没有安装. 做 FishBot 等导航、建图项目时, 重新运行一键安装选菜单 [22] 安装")
        PrintUtils.print_info("              (导航 Nav2、建图 slam_toolbox/Cartographer、键盘/手柄遥控等)")

        if ok:
            PrintUtils.print_info("  环境变量:   已写入 ~/.bashrc, 新开终端自动生效")
            cmake = "/opt/ros/{}/share/rosidl_adapter/cmake/rosidl_adapt_interfaces.cmake".format(version)
            if os.path.exists(cmake):
                with open(cmake) as f:
                    fixed = "idl_tuples ENCODING UTF-8)" in f.read()
                PrintUtils.print_info("  中文路径:   {}".format(
                    "已修复工作空间放在中文路径(如 ~/桌面)下编译消息包报错的问题" if fixed
                    else "修复没有生效, 工作空间请先放在英文路径下, 或运行菜单 [4] 重试"))
        PrintUtils.print_success("=" * 60)
