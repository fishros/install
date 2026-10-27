# -*- coding: utf-8 -*-
import os
import re
from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, AptUtils, ChooseTask, AdUtils
from .base import osversion
from .base import run_tool_file
from .base import tr


class RosVersion:
    STATUS_EOL = 0
    STATUS_LTS = 1

    def __init__(self, name, version, status, deps=[]):
        self.name = name
        self.version = version
        self.status = status
        self.deps = deps


class RosVersions:
    ros_version = [
        # ubuntu 26
        RosVersion(
            "lyrical",
            "ROS2",
            RosVersion.STATUS_LTS,
            [
                "python3-colcon-core",
                "python3-colcon-common-extensions",
                "python3-argcomplete",
                "python3-rosdep",
            ],
        ),
        # ubuntu 24
        RosVersion(
            "kilted",
            "ROS2",
            RosVersion.STATUS_LTS,
            [
                "python3-colcon-core",
                "python3-colcon-common-extensions",
                "python3-argcomplete",
                "python3-rosdep",
            ],
        ),
        RosVersion(
            "jazzy",
            "ROS2",
            RosVersion.STATUS_LTS,
            [
                "python3-colcon-core",
                "python3-colcon-common-extensions",
                "python3-argcomplete",
                "python3-rosdep",
            ],
        ),
        # ubuntu 22 & 24
        RosVersion(
            "rolling",
            "ROS2",
            RosVersion.STATUS_LTS,
            [
                "python3-colcon-core",
                "python3-colcon-common-extensions",
                "python3-argcomplete",
                "python3-rosdep",
            ],
        ),
        RosVersion(
            "eloquent",
            "ROS2",
            RosVersion.STATUS_EOL,
            [
                "python3-colcon-core",
                "python3-colcon-common-extensions",
                "python3-argcomplete",
                "python3-rosdep",
            ],
        ),
        # ubuntu 22
        RosVersion(
            "iron",
            "ROS2",
            RosVersion.STATUS_LTS,
            [
                "python3-colcon-core",
                "python3-colcon-common-extensions",
                "python3-argcomplete",
                "python3-rosdep",
            ],
        ),
        RosVersion(
            "humble",
            "ROS2",
            RosVersion.STATUS_LTS,
            [
                "python3-colcon-core",
                "python3-colcon-common-extensions",
                "python3-argcomplete",
                "python3-rosdep",
            ],
        ),
        RosVersion(
            "galactic",
            "ROS2",
            RosVersion.STATUS_LTS,
            [
                "python3-colcon-core",
                "python3-colcon-common-extensions",
                "python3-argcomplete",
                "python3-rosdep",
            ],
        ),
        # ubuntu 20
        RosVersion(
            "foxy",
            "ROS2",
            RosVersion.STATUS_EOL,
            [
                "python3-colcon-core",
                "python3-colcon-common-extensions",
                "python3-argcomplete",
                "python3-rosdep",
            ],
        ),
        RosVersion(
            "noetic",
            "ROS1",
            RosVersion.STATUS_EOL,
            ["python3-catkin-tools", "python3-rosdep"],
        ),
        # ubuntu 18
        RosVersion(
            "melodic",
            "ROS1",
            RosVersion.STATUS_LTS,
            ["python-catkin-tools", "python-rosdep"],
        ),
        RosVersion("dashing", "ROS2", RosVersion.STATUS_EOL, []),
        # ubuntu 16
        RosVersion(
            "kinetic",
            "ROS1",
            RosVersion.STATUS_EOL,
            ["python-catkin-tools", "python-rosdep"],
        ),
        RosVersion("crystal", "ROS2", RosVersion.STATUS_EOL, []),
        RosVersion("bouncy", "ROS2", RosVersion.STATUS_EOL, []),
        RosVersion("ardent", "ROS2", RosVersion.STATUS_EOL, []),
        RosVersion("lunar", "ROS2", RosVersion.STATUS_EOL, []),
    ]

    @staticmethod
    def get_version_string(name):
        for version in RosVersions.ros_version:
            if version.name == name:
                return "{}({})".format(version.name, version.version)

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
        if version == "ROS1":
            PrintUtils.print_warn(
                "小鱼，黄黄的提示：您安装的是ROS1，可以打开一个新的终端输入roscore测试！"
            )
        elif version == "ROS2":
            PrintUtils.print_warn(
                "小鱼：黄黄的提示：您安装的是ROS2,ROS2是没有roscore的，请打开新终端输入ros2测试！小鱼制作了ROS2课程，关注公众号《鱼香ROS》即可获取~"
            )

    @staticmethod
    def get_desktop_version(name):
        version = RosVersions.get_version(name).version
        if version == "ROS1":
            return "ros-{}-desktop-full".format(name)
        elif version == "ROS2":
            return "ros-{}-desktop".format(name)


key_urls = [
    "https://gitee.com/fishros/rosdistro/raw/master/ros.asc",
    "https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc",
]
# ROS 官方 GPG 公钥完整指纹, 密钥服务器兜底时使用(短指纹容易撞)
ros_key_fingerprint = "C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654"
ros_keyring = "/etc/apt/trusted.gpg.d/ros.gpg"
# 没有 gpg 时的退路: apt>=1.4(Ubuntu 18.04+) 能直接识别 trusted.gpg.d 下 ASCII 格式的 .asc 公钥
ros_keyring_asc = "/etc/apt/trusted.gpg.d/ros.asc"

ros_mirror_dic = {
    "tsinghua": {
        "ROS1": "http://mirrors.tuna.tsinghua.edu.cn/ros/ubuntu/",
        "ROS2": "http://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu/",
    },
    "mirrorz": {
        "ROS1": "http://mirrors.cernet.edu.cn/ros/ubuntu/",
        "ROS2": "http://mirrors.cernet.edu.cn/ros2/ubuntu",
    },
    "ustc": {
        "ROS1": "https://mirrors.ustc.edu.cn/ros/ubuntu/",
        "ROS2": "https://mirrors.ustc.edu.cn/ros2/ubuntu/",
    },
    "huawei": {
        "ROS1": "https://repo.huaweicloud.com/ros/ubuntu/",
        "ROS2": "https://repo.huaweicloud.com/ros2/ubuntu/",
    },
    # 阿里云的 ROS1 源停在 2021 年, 不要用; ROS2 源与官方同步, 是 EOL 系统(focal/bionic...)唯一可用的国内源
    "aliyun": {
        "ROS2": "https://mirrors.aliyun.com/ros2/ubuntu/",
    },
    "packages.ros": {
        "ROS1": "http://packages.ros.org/ros/ubuntu/",
        "ROS2": "http://packages.ros.org/ros2/ubuntu/",
    },
}


ros_dist_dic = {
    "artful": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "bionic": {
        "tsinghua",
        "ustc",
        "huawei",
        "mirrorz",
        "packages.ros",
    },
    "buster": {
        "tsinghua",
        "ustc",
        "huawei",
        "mirrorz",
        "packages.ros",
    },
    "cosmic": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "disco": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "eoan": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "focal": {
        "tsinghua",
        "ustc",
        "huawei",
        "mirrorz",
        "packages.ros",
    },
    "jessie": {
        "tsinghua",
        "ustc",
        "huawei",
        "mirrorz",
        "packages.ros",
    },
    "lucid": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "maverick": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "natty": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "oneiric": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "precise": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "quantal": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "raring": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "saucy": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "stretch": {
        "tsinghua",
        "ustc",
        "huawei",
        "mirrorz",
        "packages.ros",
    },
    "trusty": {
        "tsinghua",
        "ustc",
        "huawei",
        "mirrorz",
        "packages.ros",
    },
    "utopic": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "vivid": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "wheezy": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "wily": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "xenial": {
        "tsinghua",
        "ustc",
        "huawei",
        "mirrorz",
        "packages.ros",
    },
    "yakkety": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "zesty": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
}


# 2026-10 实测: 清华/中科大/华为/MirrorZ 的 ROS2 源里 bionic/focal/buster/xenial 的索引
# 停在 2024~2025 年, 但对应的 deb 包已被删除, apt 能看到 ros-foxy-* 却下载 404;
# 阿里云与官方源同步正常. 这几个系统的 ROS2 只保留阿里云和官方源.
ros2_dist_dic = {
    "bionic": {
        "aliyun",
        "packages.ros",
    },
    "bookworm": {
        "tsinghua",
        "ustc",
        "huawei",
        "mirrorz",
        "aliyun",
        "packages.ros",
    },
    "bullseye": {
        "tsinghua",
        "ustc",
        "huawei",
        "mirrorz",
        "aliyun",
        "packages.ros",
    },
    "buster": {
        "aliyun",
        "packages.ros",
    },
    "cosmic": {
        "packages.ros",
    },
    "disco": {
        "packages.ros",
    },
    "eoan": {
        "packages.ros",
    },
    "focal": {
        "aliyun",
        "packages.ros",
    },
    "jessie": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "jammy": {
        "tsinghua",
        "ustc",
        "huawei",
        "mirrorz",
        "aliyun",
        "packages.ros",
    },
    "noble": {
        "tsinghua",
        "ustc",
        "huawei",
        "mirrorz",
        "aliyun",
        "packages.ros",
    },
    "resolute": {
        "tsinghua",
        "ustc",
        "huawei",
        "mirrorz",
        "aliyun",
        "packages.ros",
    },
    "stretch": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "trixie": {
        "tsinghua",
        "ustc",
        "huawei",
        "mirrorz",
        "packages.ros",
    },
    "trusty": {
        "tsinghua",
        "ustc",
        "huawei",
        "packages.ros",
    },
    "xenial": {
        "aliyun",
        "packages.ros",
    },
    "utopic": {
        "packages.ros",
    },
    "yakkety": {
        "packages.ros",
    },
    "zesty": {
        "packages.ros",
    },
}


class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装ROS和ROS2,支持树莓派Jetson"
        self.type = BaseTool.TYPE_INSTALL
        self.author = "小鱼"

    def get_mirror_by_code(self, code, arch="amd64", first_choose="tsinghua", excluded=None):
        """
        获取镜像通过系统版本号
        excluded: {"ROS1": set(), "ROS2": set()} 已确认不可用的镜像, 跳过
        """
        excluded = excluded or {}
        ros1_choose_queue = [first_choose, "tsinghua", "ustc", "huawei", "packages.ros"]
        ros2_choose_queue = [
            first_choose,
            "tsinghua",
            "ustc",
            "huawei",
            "aliyun",
            "packages.ros",
        ]

        # armhf架构，优先使用官方源
        if arch == "armhf":
            ros2_choose_queue = ["packages.ros", "tsinghua", "ustc", "huawei", "aliyun"]

        mirror = []
        for version, dist_dic, queue in (
            ("ROS1", ros_dist_dic, ros1_choose_queue),
            ("ROS2", ros2_dist_dic, ros2_choose_queue),
        ):
            # 确认源里有对应的系统的，比如jammy
            if code not in dist_dic.keys():
                continue
            for item in queue:
                if item in excluded.get(version, ()):
                    continue
                if item in dist_dic[code] and version in ros_mirror_dic[item]:
                    mirror.append(ros_mirror_dic[item][version])
                    break
        return mirror

    def supported_mirrors(self):
        """当前系统可选的国内 ROS 镜像(按推荐顺序)"""
        codename = osversion.get_codename()
        return [
            mirror
            for mirror in ("ustc", "tsinghua", "huawei", "mirrorz", "aliyun")
            if mirror in ros_dist_dic.get(codename, ()) or mirror in ros2_dist_dic.get(codename, ())
        ]

    def select_mirror(self):
        """
        让用户选择镜像源, 选 [0] 返回 BaseTool.BACK
        """
        mirror_names = {
            "ustc": "中科大镜像源 (推荐国内用户使用)",
            "tsinghua": "清华镜像源 (容易被封禁)",
            "huawei": "华为镜像源",
            "mirrorz": "MirrorZ 校园网联合镜像站",
            "aliyun": "阿里云镜像源 (仅ROS2, Ubuntu20.04/18.04 装ROS2请选它)",
        }
        supported_mirrors = self.supported_mirrors()

        # 只有官方源或只有一个国内源时不再询问
        if len(supported_mirrors) <= 1:
            default = supported_mirrors[0] if supported_mirrors else "packages.ros"
            PrintUtils.print_info("您的系统默认使用镜像源: {}".format(default))
            return default

        mirror_dict = {}
        for count, mirror in enumerate(supported_mirrors, 1):
            mirror_dict[count] = mirror_names[mirror]
        official = len(supported_mirrors) + 1
        mirror_dict[official] = "ROS官方源 (国外用户或需要最新版本时使用)"

        code, result = ChooseTask(
            mirror_dict,
            "检测到您的系统支持多个ROS镜像源，请选择您想要使用的ROS镜像源：",
        ).run()
        if code == 0:
            return BaseTool.BACK
        if code == official:
            return "packages.ros"
        return supported_mirrors[code - 1]

    def write_ros_source(self, arch, codename, mirrors):
        source_data = ""
        for mirror in mirrors:
            source_data += "deb [arch={}]  {} {} main\n".format(arch, mirror, codename)
        FileUtils.delete("/etc/apt/sources.list.d/ros-fish.list")
        FileUtils.new("/etc/apt/sources.list.d/", "ros-fish.list", source_data)
        self.ros_mirrors = mirrors

    @staticmethod
    def has_command(name):
        return CmdTask("command -v {}".format(name), 5).run()[0] == 0

    def http_status(self, url):
        """
        返回 url 跟随跳转后的 HTTP 状态码, 取不到返回空串.
        Ubuntu 22.04/24.04 桌面版默认没装 curl, 系统源坏了又装不上时用 wget 兜底.
        带上 apt 的 User-Agent: 中科大镜像对 wget 默认 UA 一律返回 403, 会被误判成包已删除
        """
        user_agent = "Debian APT-HTTP/1.3"
        if self.has_command("curl"):
            check = CmdTask(
                "curl -sIL -A '{}' -o /dev/null -w '%{{http_code}}' --max-time 15 '{}'".format(user_agent, url), 20
            ).run()
            return "".join(check[1]).strip()
        check = CmdTask(
            "wget --spider -S -U '{}' --timeout=15 --tries=1 '{}' 2>&1 | grep 'HTTP/'".format(user_agent, url), 20
        ).run()
        codes = re.findall(r"HTTP/[\d.]+ (\d+)", " ".join(check[1]))
        return codes[-1] if codes else ""

    def find_stale_mirrors(self, ros_pkg):
        """
        国内镜像有时只剩索引、包文件已被删除, apt update 正常, 一安装就满屏 404.
        这里对每个 ROS 版本抽一个 ros-base 包发 HEAD 请求, 确认真的能下载.
        返回 {"ROS1"/"ROS2": 镜像名}, 只包含确认 404 的镜像
        """
        stale = {}
        for distro_name in set(ros_pkg.values()):
            # get_all_instsll_ros_pkgs 返回的是 "foxy" 这样的版本名, 换成真实包名
            pkg = "ros-{}-ros-base".format(distro_name)
            result = CmdTask(
                "apt-get download --print-uris {} 2>/dev/null | head -n 1".format(pkg), 20
            ).run()
            uri = re.findall(r"'([^']+\.deb)'", " ".join(result[1]))
            if not uri:
                continue
            uri = uri[0]
            http_code = self.http_status(uri)
            # 只认明确的 403/404/410, 网络超时(000)等不算, 避免误判
            if http_code not in ("403", "404", "410"):
                continue
            plain_uri = uri.replace("https://", "http://")
            for name, urls in ros_mirror_dic.items():
                for version, url in urls.items():
                    if plain_uri.startswith(url.replace("https://", "http://")):
                        stale[version] = name
                        PrintUtils.print_warn(
                            "检测到{}镜像源[{}]索引已过期, 包文件下载返回{}: {}".format(
                                version, name, http_code, uri
                            )
                        )
        return stale

    def auto_mirror_order(self, codename):
        """
        全自动模式下的镜像尝试顺序: 国外直接用官方源; 国内按测速结果排列国内镜像, 官方源兜底
        """
        names = [
            name
            for name in ("ustc", "tsinghua", "huawei", "mirrorz", "aliyun")
            if name in ros_dist_dic.get(codename, ()) or name in ros2_dist_dic.get(codename, ())
        ]
        if not names or (tr is not None and not tr.isCN()):
            return ["packages.ros"] + names
        url_to_name = {}
        for name in names:
            url = ros_mirror_dic[name].get("ROS2") or ros_mirror_dic[name].get("ROS1")
            url_to_name[url] = name
        PrintUtils.print_info("正在为您测速挑选最快的ROS镜像源...")
        ordered = [url_to_name[url] for url in AptUtils.get_fast_url(list(url_to_name.keys()))]
        return ordered + ["packages.ros"]

    def add_source(self, auto=False):
        """
        检查并添加ROS系统源
        auto: 全自动模式, 不询问用户, 按测速顺序自动尝试, 失败自动换下一个
        """
        arch = AptUtils.getArch()
        if arch == None:
            return False
        codename = osversion.get_codename()

        if auto:
            candidates = self.auto_mirror_order(codename)
            selected_mirror = candidates[0]
            PrintUtils.print_info("自动选择的ROS镜像源: {}".format(selected_mirror))
        else:
            # 让用户选择镜像源
            selected_mirror = self.select_mirror()
            if selected_mirror == BaseTool.BACK:
                return BaseTool.BACK
            PrintUtils.print_info("您选择的镜像源: {}".format(selected_mirror))
        excluded = {"ROS1": set(), "ROS2": set()}

        for attempt in range(8):
            mirrors = self.get_mirror_by_code(
                codename, arch=arch, first_choose=selected_mirror, excluded=excluded
            )
            if not mirrors:
                break
            PrintUtils.print_info("根据您的系统和选择，为您推荐安装源为{}".format(mirrors))
            self.write_ros_source(arch, codename, mirrors)

            ros_pkg = self.get_all_instsll_ros_pkgs()
            if ros_pkg:
                stale = self.find_stale_mirrors(ros_pkg)
                if not stale:
                    if auto:
                        PrintUtils.print_success("ROS软件源添加成功")
                    else:
                        PrintUtils.print_success(
                            "恭喜，成功添加ROS源，接下来可以使用apt安装ROS或者使用[1]一键安装ROS安装！"
                        )
                    return True
                for version, name in stale.items():
                    excluded[version].add(name)
                PrintUtils.print_warn("自动切换到下一个可用的镜像源重试...")
                continue

            # apt update 失败或搜不到 ROS 包, 换一个镜像源再试
            for version in excluded.keys():
                excluded[version].add(selected_mirror)
            if auto:
                remaining = [m for m in candidates if m not in excluded["ROS2"]]
                if not remaining:
                    break
                selected_mirror = remaining[0]
                PrintUtils.print_warn("换源后更新失败, 自动换用镜像源: {}".format(selected_mirror))
                continue
            PrintUtils.print_warn("换源后更新失败，您可以重新选择镜像源再尝试！")
            selected_mirror = self.select_mirror()
            if selected_mirror == BaseTool.BACK:
                return BaseTool.BACK
            PrintUtils.print_info("您重新选择的镜像源: {}".format(selected_mirror))
            for version in excluded.keys():
                excluded[version].discard(selected_mirror)

        PrintUtils.print_error(
            "多次换源后仍然失败，请携带 /tmp/fishros_install.log 到鱼香社区 https://fishros.org.cn/forum 一键安装板块反馈！"
        )
        return False

    @staticmethod
    def key_sources():
        """
        公钥下载地址, 按可靠程度排序. 第一个是随一键安装一起发布的公钥(tools/keys/ros.asc):
        用户既然能下载到一键安装, 就一定能从同一台服务器下载到它
        """
        prefix = os.environ.get("FISHROS_URL", "http://mirror.fishros.com/install/")
        return [os.path.join(prefix, "tools/keys/ros.asc")] + key_urls

    @staticmethod
    def gpg_cmd(*commands):
        """
        拼出一段 shell: 依次执行若干条 gpg 命令, 都用同一个临时目录当 GNUPGHOME, 结束后删掉.
        全新系统里 root 从没用过 gpg, /root/.gnupg 不存在, gpg 连密钥服务器时起不来 dirmngr
        ("缺少 dirmngr"), 导入/校验也会因为建不了锁文件失败
        """
        gpg = 'sudo env GNUPGHOME="$d" gpg --batch '
        body = " && ".join(gpg + c for c in commands)
        return "sh -c 'd=$(mktemp -d) && {}; r=$?; rm -rf \"$d\"; exit $r'".format(body)

    def key_fingerprint_ok(self, key_file):
        """校验公钥是不是 ROS 官方那把; 没有 gpg 时只能跳过"""
        if not self.has_command("gpg"):
            return True
        result = CmdTask(
            self.gpg_cmd("--with-colons --import-options show-only --import {}".format(key_file)), 20
        ).run()
        return ros_key_fingerprint in " ".join(result[1])

    def download_ros_key(self):
        """
        依次尝试各个公钥地址, 每个地址最多试 3 次(网络抖动时 TLS 连接会被重置, curl 的 --retry 不重试这种错误),
        内容是 PGP 公钥且指纹正确才采用, 返回本地文件路径
        """
        key_file = "/tmp/fishros_ros.asc"
        # wget 一定有(用户就是用它下载的一键安装), curl 不一定; gitee 会 302 跳转, curl 必须带 -L
        if self.has_command("curl"):
            download = "curl -fsSL --max-time 30 {url} -o {out}"
        else:
            download = "wget -q --timeout=30 -O {out} {url}"
        sources = self.key_sources()
        PrintUtils.print_success(tr.tr("正在获取ROS公钥:{}").format(sources))
        for key_url in sources:
            for attempt in range(3):
                CmdTask("rm -f {}".format(key_file), 3).run()
                if CmdTask(download.format(url=key_url, out=key_file), 40).run()[0] != 0:
                    continue
                if CmdTask("grep -q 'BEGIN PGP PUBLIC KEY BLOCK' {}".format(key_file), 3).run()[0] != 0:
                    PrintUtils.print_warn("{} 返回的不是公钥, 尝试下一个地址".format(key_url))
                    break
                if not self.key_fingerprint_ok(key_file):
                    PrintUtils.print_warn("{} 的公钥指纹不对, 不予采用".format(key_url))
                    break
                PrintUtils.print_success(tr.tr("已获取ROS公钥:{}").format(key_url))
                self.key_source = key_url
                return key_file
        return None

    def add_key(self):
        PrintUtils.print_success(
            tr.tr("============正在添加ROS源密钥=================")
        )
        # check apt
        if not AptUtils.checkapt():
            pass
        # install dep
        AptUtils.install_pkg("curl")
        AptUtils.install_pkg("gnupg2")

        cmd_result = (1, [], [])
        key_file = self.download_ros_key()
        if key_file:
            # 统一导入 trusted.gpg.d, 新旧系统都认, 不依赖已弃用的 apt-key
            if self.has_command("gpg"):
                cmd_result = CmdTask(
                    "{} && sudo chmod 644 {}".format(
                        self.gpg_cmd("--yes --dearmor -o {} {}".format(ros_keyring, key_file)), ros_keyring
                    ),
                    20,
                ).run()
            if cmd_result[0] != 0:
                # 没有 gpg(精简系统/容器, 或系统源坏了装不上 gnupg)时直接放 .asc 公钥
                PrintUtils.print_info("gpg 不可用, 改为直接导入 ASCII 格式公钥")
                cmd_result = CmdTask(
                    "sudo rm -f {0} && sudo cp {1} {2} && sudo chmod 644 {2}".format(
                        ros_keyring, key_file, ros_keyring_asc
                    ),
                    10,
                ).run()
            if cmd_result[0] != 0 and self.has_command("apt-key"):
                cmd_result = CmdTask("sudo apt-key add {}".format(key_file), 20).run()

        if cmd_result[0] != 0 and self.has_command("gpg"):
            PrintUtils.print_info(tr.tr("导入密钥失败，开始更换导入方式并二次尝试..."))
            # 从密钥服务器取, 用完整指纹; 有的网络 80 端口不通、有的 11371 端口不通, 两个都试
            for keyserver in ("hkp://keyserver.ubuntu.com:80", "hkp://keyserver.ubuntu.com"):
                cmd_result = CmdTask(
                    "{} | sudo tee {} > /dev/null && sudo chmod 644 {}".format(
                        self.gpg_cmd(
                            "--keyserver {} --recv-keys {} >&2".format(keyserver, ros_key_fingerprint),
                            "--export {}".format(ros_key_fingerprint),
                        ),
                        ros_keyring,
                        ros_keyring,
                    ),
                    60,
                ).run()
                if cmd_result[0] == 0 and CmdTask("test -s {}".format(ros_keyring), 3).run()[0] == 0:
                    break
                cmd_result = (1, [], [])
            if cmd_result[0] != 0:
                # 取不到时 tee 会留下空文件, apt 会对它报警告, 删掉
                CmdTask("[ -s {0} ] || sudo rm -f {0}".format(ros_keyring), 3).run()

        if cmd_result[0] != 0:
            PrintUtils.print_error(
                tr.tr("获取密钥失败")
                + ", 后续 apt update 可能报 NO_PUBKEY, 请检查网络后重试"
            )
        return cmd_result

    def check_sys_source(self):
        """高手模式第一步: 问要不要换系统源(会先检测当前系统源是国内还是国外再给建议), 选 [0] 返回 BaseTool.BACK"""
        tool = run_tool_file("tools.tool_config_system_source", authorun=False)
        return tool.ask_change_before_install()

    def get_all_instsll_ros_pkgs(self):
        AptUtils.checkapt()
        dic_base = AptUtils.search_package(
            "ros-base", "ros-[A-Za-z]+-ros-base", "ros-", "-base"
        )
        if dic_base == None:
            return None
        ros_name = {}
        for a in dic_base.keys():
            ros_name[RosVersions.get_version_string(a)] = a
        if len(ros_name) == 0:
            return None
        return ros_name

    def support_install(self):
        # check support
        if (osversion.get_codename() not in ros_dist_dic.keys()) and (
            osversion.get_codename() not in ros2_dist_dic.keys()
        ):
            PrintUtils.print_error(
                "小鱼:检测当前系统{}{}:{} 暂不支持一键安装ROS,请关注公众号《鱼香ROS》获取帮助.".format(
                    osversion.get_name(),
                    osversion.get_version(),
                    osversion.get_codename(),
                )
            )
            return False
        PrintUtils.print_success(
            "小鱼:检测当前系统{}{}:{} 支持一键安装ROS".format(
                osversion.get_name(), osversion.get_version(), osversion.get_codename()
            )
        )
        return True

    def install_success(self, name):
        """
        检查某个版本的ROS是否安装成功
        """
        result = CmdTask("ls /opt/ros/{}/setup.bash".format(name), 0).run()
        if str(result[1]).find("setup.bash") >= 1:
            return True
        return False

    def choose_ros_version(self):
        """
        选择 ROS 版本. 返回 (版本名, dic_base); 选 [0] 返回 BaseTool.BACK; 软件源里搜不到 ROS 时返回 None
        """
        dic_base = AptUtils.search_package(
            "ros-base", "ros-[A-Za-z]+-ros-base", "ros-", "-base"
        )
        if dic_base == None:
            return None

        ros_name = {}
        for a in dic_base.keys():
            ros_name[RosVersions.get_version_string(a)] = a

        code, rosname = ChooseTask(
            ros_name.keys(), "请选择你要安装的ROS版本名称(请注意ROS1和ROS2区别):", True
        ).run()
        if code == 0:
            PrintUtils.print_delay(
                "是因为没有自己想要的ROS版本吗？ROS版本和操作系统版本是有对应关系的哦，所以可能是你的系统版本{}不对!具体请查看：https://fishros.org.cn/forum/topic/96".format(
                    str(str(osversion.get_name()) + str(osversion.get_version()))
                ),
                0.001,
            )
            return BaseTool.BACK
        return ros_name[rosname], dic_base

    def choose_ros_kind(self, version):
        """桌面版还是基础版, 返回 1(桌面版) / 2(基础版); 选 [0] 返回 BaseTool.BACK"""
        rosname = RosVersions.get_version_string(version)
        version_dic = {1: rosname + "桌面版", 2: rosname + "基础版(小)"}
        code, name = ChooseTask(
            version_dic, "请选择安装的具体版本(如果不知道怎么选,请选1桌面版):", False
        ).run()
        return BaseTool.BACK if code == 0 else code

    def install_ros_packages(self, install_version, code, dic_base):
        """
        安装指定版本的ROS, 自定义模式和全自动模式共用
        install_version: 版本名, 如 humble; code: 1 桌面版, 2 基础版; dic_base: 版本名 -> ros-base 包名
        """
        install_tool = "aptitude"
        install_tool_apt = "apt"
        if osversion.get_version() == "16.04":
            install_tool = "apt"

        if install_tool == "aptitude":
            AptUtils.install_pkg("aptitude")
        AdUtils.show("installing")

        # ======================================================基础版本==============================================================
        if code == 2:
            # 第一次尝试
            cmd_result = CmdTask(
                "sudo {} install  {} -y".format(
                    install_tool_apt, dic_base[install_version]
                ),
                300,
                os_command=True,
            ).run()
            cmd_result = CmdTask(
                "sudo {} install  {} -y".format(
                    install_tool_apt, dic_base[install_version]
                ),
                300,
                os_command=False,
            ).run()
            if FileUtils.check_result(
                cmd_result,
                ["未满足的依赖关系", "unmet dependencies", "but it is not installable"],
            ):
                # 尝试使用aptitude解决依赖问题
                PrintUtils.print_warn(
                    "============================================================"
                )
                PrintUtils.print_delay(
                    "请注意我，检测你在安装过程中出现依赖问题，请在稍后输入n,再选择y,即可解决"
                )
                import time

                input("确认了解情况，请输入回车继续安装")
                cmd_result = CmdTask(
                    "sudo {} install   {} ".format(
                        install_tool, dic_base[install_version]
                    ),
                    300,
                    os_command=True,
                ).run()
                cmd_result = CmdTask(
                    "sudo {} install   {} -y".format(
                        install_tool, dic_base[install_version]
                    ),
                    300,
                    os_command=False,
                ).run()

        # ======================================================桌面版本==============================================================
        elif code == 1:
            cmd_result = CmdTask(
                "sudo {} install   {} -y".format(
                    install_tool_apt, RosVersions.get_desktop_version(install_version)
                ),
                300,
                os_command=True,
            ).run()
            cmd_result = CmdTask(
                "sudo {} install   {} -y".format(
                    install_tool_apt, RosVersions.get_desktop_version(install_version)
                ),
                300,
                os_command=False,
            ).run()
            if FileUtils.check_result(
                cmd_result,
                ["未满足的依赖关系", "unmet dependencies", "but it is not installable"],
            ):
                # 尝试使用aptitude解决依赖问题
                PrintUtils.print_warn(
                    "============================================================"
                )
                PrintUtils.print_delay(
                    "请注意我，检测你在安装过程中出现依赖问题，请在稍后输入n,再选择y,即可解决（若无法解决，清在稍后手动运行命令: sudo aptitude install {})".format(
                        RosVersions.get_desktop_version(install_version)
                    )
                )
                import time

                input("确认了解情况，请输入回车继续安装")
                cmd_result = CmdTask(
                    "sudo {} install   {}".format(
                        install_tool, RosVersions.get_desktop_version(install_version)
                    ),
                    300,
                    os_command=True,
                ).run()
                cmd_result = CmdTask(
                    "sudo {} install   {} -y".format(
                        install_tool, RosVersions.get_desktop_version(install_version)
                    ),
                    300,
                    os_command=False,
                ).run()

        # 个别包下载中断(网络抖动/镜像临时不可用)时, 刷新索引后补下一次
        if cmd_result[0] != 0 and FileUtils.check_result(
            cmd_result, ["Unable to fetch some archives", "--fix-missing", "无法下载"]
        ):
            PrintUtils.print_warn("部分软件包下载失败, 刷新软件源后重试一次...")
            CmdTask("sudo apt update", 100).run()
            target = (
                dic_base[install_version]
                if code == 2
                else RosVersions.get_desktop_version(install_version)
            )
            cmd_result = CmdTask(
                "sudo {} install --fix-missing {} -y".format(install_tool_apt, target),
                300,
                os_command=False,
            ).run()

        # apt broken error
        if cmd_result[0] != 0:
            if FileUtils.check_result(cmd_result, ["--fix-broken install"]):
                CmdTask("sudo apt --fix-broken install -y").run()
                # rosname 是 "foxy(ROS2)" 这种展示名, 包名要用 install_version 换算
                if code == 2:
                    cmd_result = CmdTask(
                        "sudo {} install   {} -y".format(
                            install_tool_apt, dic_base[install_version]
                        ),
                        300,
                        os_command=False,
                    ).run()
                elif code == 1:
                    cmd_result = CmdTask(
                        "sudo {} install   {} -y".format(
                            install_tool_apt,
                            RosVersions.get_desktop_version(install_version),
                        ),
                        300,
                        os_command=False,
                    ).run()

        if cmd_result[0] != 0 and FileUtils.check_result(
            cmd_result, [r"404\s+Not Found"]
        ):
            PrintUtils.print_warn(
                "安装过程中出现 404, 说明当前ROS镜像源缺包, 请重新运行一键安装并换一个ROS镜像源(阿里云或ROS官方源)"
            )

        self.last_install_result = cmd_result

        # 安装额外的依赖
        RosVersions.install_depend(install_version)

        return install_version

    def config_env_and_tip(self, version_name):
        """
        配置系统源
        """
        if self.install_success(version_name):
            run_tool_file("tools.tool_config_rosenv")
            PrintUtils.print_success(
                "恭喜你，安装成功了，再附赠你机器人学习宝藏网站：鱼香社区:https://fishros.org.cn/forum"
            )
        else:
            AdUtils.mark_failed()
            PrintUtils.print_error(
                "安装失败了,请打开鱼香社区：https://fishros.org.cn/forum 在一键安装专区反馈问题..."
            )

    def install_ros(self):
        """
        高手模式: 依次选择 系统源 -> ROS镜像源 -> ROS版本 -> 桌面版/基础版, 然后安装.
        每一步选 [0] 都退回前一步, 在第一步退回时返回 BaseTool.BACK
        """
        PrintUtils.print_delay("欢迎使用ROS开箱子工具，本工具由[鱼香ROS]小鱼贡献..")
        if not self.support_install():
            return False

        AptUtils.wait_and_repair()
        step, forward, key_added = 0, True, False
        version, dic_base, kind = None, None, None
        while step < 4:
            if step < 0:
                return BaseTool.BACK
            if step == 0:
                result = self.check_sys_source()
            elif step == 1:
                # 只有一个可选镜像时这一步不提问, 从下一步退回来时直接再往前退, 否则会卡在两步之间
                if not forward and len(self.supported_mirrors()) <= 1:
                    step -= 1
                    continue
                if not key_added:
                    self.add_key()
                    key_added = True
                result = self.add_source()
                if result is False:
                    return False
            elif step == 2:
                result = self.choose_ros_version()
                if result is None:
                    return False
                if result != BaseTool.BACK:
                    version, dic_base = result
            else:
                result = self.choose_ros_kind(version)
                kind = result
            forward = result != BaseTool.BACK
            step += 1 if forward else -1

        self.install_ros_packages(version, kind, dic_base)
        self.config_env_and_tip(version)
        if self.install_success(version):
            RosVersions.tip_test_command(version)
            AdUtils.show("ros_installed")

    def run(self):
        # 网上的教程都写"输入 1", 所以小白模式也放在菜单 1 里, 进来先选模式
        while True:
            code, _ = ChooseTask(
                {
                    1: "小白模式(推荐): 自动识别系统, 自动换源、选版本, 中途不用再做选择, 装完列出帮你选了什么",
                    2: "高手模式: 自己选择系统源、ROS镜像源、ROS版本和安装内容",
                },
                "请选择安装模式(不知道怎么选就选1):",
            ).run()
            if code == 0:
                return BaseTool.BACK
            if code == 1:
                result = run_tool_file("tools.tool_install_ros_auto", authorun=False).run()
            else:
                result = self.install_ros()
            # 在模式里的第一步选了返回上一步, 回到选模式
            if result != BaseTool.BACK:
                return result
