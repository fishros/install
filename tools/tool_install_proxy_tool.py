# -*- coding: utf-8 -*-
import collections
import os
import shutil
import sys
import time
import urllib.request
from urllib.parse import quote

from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, ChooseTask
from .base import osarch

# 可选的客户端. port 是各客户端默认的混合代理端口, 写进 proxy_add 快捷命令
# (Clash Verge Rev 默认是 7897 不是 7890, 原来一律写 7890, 装它的用户 proxy_add 用不了)
CLIENTS = {
    1: {
        "name": "FlClash",
        "tip": "FlClash(推荐): 有界面, 安装包最小(约40MB)",
        "repo": "chen08209/FlClash",
        "tag": "v0.9.2",
        "cdn_dir": "FlClash/v0.9.2",
        "file": "FlClash-0.9.2-linux-{arch}.deb",
        "port": 7890,
        "cmds": ["FlClash", "flclash"],
    },
    2: {
        "name": "Clash Verge Rev",
        "tip": "Clash Verge Rev: 有界面(约100MB)",
        "repo": "clash-verge-rev/clash-verge-rev",
        "tag": "v2.5.8",
        "cdn_dir": "clash-verge-rev/Clash%20Verge%20Rev%20v2.5.8",
        "file": "Clash.Verge_2.5.8_{arch}.deb",
        "port": 7897,
        "cmds": ["clash-verge", "clash-verge-rev"],
    },
}

# 国内直连 GitHub 基本下不动, 按顺序尝试: 两个公共 GitHub 加速站(快但时好时坏, 有时会拒绝某些仓库),
# 最后用 repo.trojan-cdn.com 兜底(一直能下, 但国内只有十几 KB/s). 2026-11 在国内服务器实测
DOWNLOAD_SOURCES = [
    ("ghfast.top 加速", "https://ghfast.top/https://github.com/{repo}/releases/download/{tag}/{file}"),
    ("gh-proxy.com 加速", "https://gh-proxy.com/https://github.com/{repo}/releases/download/{tag}/{file}"),
    ("trojan-cdn 镜像", "https://repo.trojan-cdn.com/{cdn_dir}/{file}"),
]
# 每个源先下 15 秒, 平均速度达到 200KB/s 就用它下完; 都达不到时, 用测下来最快的那个源下完
# (不能简单地「慢了就换下一个」: 实测 gh-proxy.com 89KB/s 被放弃, 最后落到只有 15KB/s 的 trojan-cdn, 反而更慢)
SLOW_CHECK_SECONDS = 15
SLOW_SPEED = 200 * 1024


class Tool(BaseTool):
    RECOMMEND_SUBSCRIBE_URL = "https://fishros.org.cn/forum/topic/668"

    def __init__(self):
        self.name = "一键安装 Linux 代理科学上网工具"
        self.type = BaseTool.TYPE_INSTALL
        self.author = "小鱼"

    def _run_cmd(self, cmd, timeout=0, msg=None):
        if msg:
            PrintUtils.print_info(msg)
        return CmdTask(cmd, timeout).run()

    def _code(self, result):
        if isinstance(result, tuple) and len(result) > 0:
            return result[0]
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return -1

    def _out(self, result):
        if (
            isinstance(result, tuple)
            and len(result) > 1
            and isinstance(result[1], list)
        ):
            return result[1]
        return []

    def _choose_install_mode(self):
        mode_dic = {code: client["tip"] for code, client in CLIENTS.items()}
        code, _ = ChooseTask(mode_dic, "请选择代理工具(不知道选哪个就选1):", False).run()
        return code

    @staticmethod
    def _format_speed(speed):
        if speed >= 1048576:
            return "{:.1f}MB/s".format(speed / 1048576.0)
        return "{:.0f}KB/s".format(speed / 1024.0)

    @staticmethod
    def _draw_progress(done, total, speed):
        """在同一行画进度条: [████████░░░░░░░░]  45%  17.5/38.7MB  2.4MB/s  剩余 9s"""
        if total:
            left = (total - done) / speed if speed > 0 else -1
            eta = "--" if left < 0 else ("{}m{:02d}s".format(int(left) // 60, int(left) % 60) if left >= 60 else "{}s".format(int(left)))
            info = " {:3.0f}%  {:.1f}/{:.1f}MB  {}  剩余 {}".format(
                done * 100.0 / total, done / 1048576.0, total / 1048576.0, Tool._format_speed(speed), eta)
            # 进度条宽度随终端宽度变化; info 里的「剩余」两个汉字各占 2 列, 多留几列余量免得折行
            width = max(10, min(40, shutil.get_terminal_size((80, 20)).columns - len(info) - 10))
            filled = int(width * done / total)
            line = "  [{}{}]{}".format("█" * filled, "░" * (width - filled), info)
        else:
            line = "  已下载 {:.1f}MB  {}".format(done / 1048576.0, Tool._format_speed(speed))
        sys.stdout.write("\r" + line + "   ")
        sys.stdout.flush()

    @staticmethod
    def _download_from(url, path, give_up_if_slow):
        """
        下载到 path, 返回 (是否下完, 平均速度 B/s). give_up_if_slow 时, 下了 SLOW_CHECK_SECONDS 秒平均速度还太慢就放弃.
        不走环境变量里的代理(和原来 wget --no-proxy 一致), 超时 15 秒
        """
        speed = 0
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        request = urllib.request.Request(url, headers={"User-Agent": "Wget/1.21"})
        # 在终端里每 0.2 秒刷新一次; 输出被重定向到文件(日志、自动化测试)时 5 秒一次, 免得刷屏
        interval = 0.2 if sys.stdout.isatty() else 5
        try:
            with opener.open(request, timeout=15) as resp, open(path, "wb") as f:
                total = int(resp.headers.get("Content-Length") or 0)
                done, start, last_print = 0, time.time(), 0
                recent = collections.deque([(start, 0)])  # 最近约 2 秒的 (时间, 已下载), 算实时速度
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    done += len(chunk)
                    now = time.time()
                    used = now - start
                    speed = done / max(used, 0.001)  # 平均速度, 用来判断这个源快不快
                    recent.append((now, done))
                    while len(recent) > 2 and now - recent[0][0] > 2:
                        recent.popleft()
                    if now - last_print >= interval:
                        last_print = now
                        span = now - recent[0][0]
                        Tool._draw_progress(done, total, (done - recent[0][1]) / span if span > 0 else speed)
                    if give_up_if_slow and used > SLOW_CHECK_SECONDS and speed < SLOW_SPEED:
                        print("")
                        PrintUtils.print_warn("速度较慢({}), 先试试下一个下载源".format(Tool._format_speed(speed)))
                        return False, speed
            Tool._draw_progress(done, total, speed)
            print("")
            return (total == 0 or done == total), speed
        except Exception as e:
            print("")
            PrintUtils.print_warn("下载失败: {}".format(e))
            return False, 0

    def _download_package(self, client, path):
        """按 DOWNLOAD_SOURCES 的顺序尝试, 下到完整的 deb 就返回 True"""
        params = dict(client, file=client["file"].format(arch=osarch))
        slow_sources = []
        for source_name, template in DOWNLOAD_SOURCES:
            url = template.format(**params)
            PrintUtils.print_info("从 {} 下载: {}".format(source_name, url))
            ok, speed = self._download_from(url, path, give_up_if_slow=True)
            if ok and self._code(CmdTask('dpkg-deb -f "{}" Package'.format(path)).run()) == 0:
                return True
            if speed > 0:
                slow_sources.append((speed, source_name, url))
        # 没有一个源够快: 用测下来最快的那个下完
        for speed, source_name, url in sorted(slow_sources, reverse=True):
            PrintUtils.print_warn("几个下载源都比较慢, 改用其中最快的 {}({}) 下完, 请耐心等待".format(source_name, self._format_speed(speed)))
            ok, _ = self._download_from(url, path, give_up_if_slow=False)
            if ok and self._code(CmdTask('dpkg-deb -f "{}" Package'.format(path)).run()) == 0:
                return True
        return False

    def _install_deb_package(self, client):
        temp_file = "/tmp/fishros_proxy_tool.deb"
        if not self._download_package(client, temp_file):
            self._run_cmd('rm -f "{}"'.format(temp_file), 10)
            return False

        install = self._run_cmd(
            'sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "{}"'.format(
                temp_file
            ),
            300,
            "安装代理工具中(自动处理依赖)...",
        )
        if self._code(install) == 0:
            self._run_cmd('rm -f "{}"'.format(temp_file), 10)
            return True

        PrintUtils.print_warn("apt安装失败，回退到dpkg+fix-broken方案...")
        dpkg_install = self._run_cmd(
            'sudo dpkg -i "{}"'.format(temp_file), 180, "使用dpkg安装中..."
        )
        if self._code(dpkg_install) != 0:
            fix_dep = self._run_cmd(
                "sudo DEBIAN_FRONTEND=noninteractive apt-get --fix-broken install -y",
                600,
                "修复依赖中...",
            )
            if self._code(fix_dep) != 0:
                self._run_cmd('rm -f "{}"'.format(temp_file), 10)
                return False

        final_install = self._run_cmd(
            'sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "{}"'.format(
                temp_file
            ),
            300,
            "再次确认代理工具安装状态...",
        )
        if self._code(final_install) != 0:
            self._run_cmd('rm -f "{}"'.format(temp_file), 10)
            return False

        self._run_cmd('rm -f "{}"'.format(temp_file), 10)
        return True

    def _read_input_subscription(self):
        PrintUtils.print_warn(
            "请输入订阅地址(若无请访问 {} 获取)".format(self.RECOMMEND_SUBSCRIBE_URL)
        )
        return input("订阅地址:").strip()

    def _auto_import_subscription(self, subscribe_url):
        encoded = quote(subscribe_url, safe="")
        clash_link = "clash://install-config?url={}".format(encoded)
        PrintUtils.print_info("正在尝试一键导入订阅...")
        result = self._run_cmd('xdg-open "{}"'.format(clash_link), 20)
        if self._code(result) == 0:
            PrintUtils.print_success("已触发一键导入，请在客户端中确认")
            return True

        PrintUtils.print_warn("自动导入失败，可能是系统未注册 clash:// 协议")
        PrintUtils.print_info("可手动复制以下链接到浏览器地址栏打开:")
        PrintUtils.print_info(clash_link)
        return False

    def _setup_proxy_alias(self, user_home, port):
        bashrc = os.path.join(user_home.rstrip("/"), ".bashrc")
        if not os.path.exists(bashrc):
            FileUtils.new(user_home.rstrip("/") + "/", name=".bashrc", data="")

        start_flag = "# >>> fishros proxy alias >>>"
        end_flag = "# <<< fishros proxy alias <<<"
        # 端口是所选客户端的默认端口, 在客户端里改过端口的话改这里的 FISHROS_PROXY_PORT 即可
        block = (
            "{start}\n"
            "FISHROS_PROXY_PORT={port}\n"
            "proxy_add(){{\n"
            "  export http_proxy=http://127.0.0.1:$FISHROS_PROXY_PORT\n"
            "  export https_proxy=http://127.0.0.1:$FISHROS_PROXY_PORT\n"
            "  export all_proxy=socks5://127.0.0.1:$FISHROS_PROXY_PORT\n"
            "  echo \"proxy on: 127.0.0.1:$FISHROS_PROXY_PORT\"\n"
            "}}\n"
            "proxy_off(){{\n"
            "  unset http_proxy https_proxy all_proxy\n"
            "  echo 'proxy off'\n"
            "}}\n"
            "proxy_status(){{\n"
            '  echo "http_proxy=$http_proxy"\n'
            '  echo "https_proxy=$https_proxy"\n'
            '  echo "all_proxy=$all_proxy"\n'
            "}}\n"
            "{end}"
        ).format(start=start_flag, end=end_flag, port=port)

        with open(bashrc, "r") as f:
            data = f.read()

        start_idx = data.find(start_flag)
        end_idx = data.find(end_flag)
        if start_idx >= 0 and end_idx >= 0 and end_idx > start_idx:
            data = data[:start_idx] + data[end_idx + len(end_flag) :]

        if len(data) > 0 and not data.endswith("\n"):
            data += "\n"
        data += block + "\n"

        with open(bashrc, "w") as f:
            f.write(data)

        PrintUtils.print_success("已写入终端快捷命令: proxy_add/proxy_off/proxy_status(端口 {})".format(port))

    def _which(self, name):
        result = self._run_cmd("command -v {}".format(name), 10)
        if self._code(result) == 0 and len(self._out(result)) > 0:
            return str(self._out(result)[0]).strip()
        return None

    def _print_launch_tips(self, client):
        PrintUtils.print_delay("==========使用方法===========")
        cmd_path = None
        for cmd in client["cmds"]:
            cmd_path = cmd_path or self._which(cmd)
        if cmd_path:
            PrintUtils.print_delay("1.启动客户端: 在应用菜单中搜索 {}, 或终端运行 {}".format(client["name"], cmd_path))
        else:
            PrintUtils.print_delay("1.启动客户端: 在应用菜单中搜索 {}".format(client["name"]))

        PrintUtils.print_delay("2.开启终端代理: proxy_add")
        PrintUtils.print_delay("3.关闭终端代理: proxy_off")
        PrintUtils.print_delay("4.查看终端代理: proxy_status")
        PrintUtils.print_delay("5.若命令未生效，请执行: source ~/.bashrc")

    def install_proxy_tool(self):
        mode = self._choose_install_mode()
        if mode == 0:
            return BaseTool.BACK
        if mode not in CLIENTS:
            PrintUtils.print_warn("已取消安装")
            return False
        if osarch not in ["amd64", "arm64"]:
            PrintUtils.print_error("当前仅支持 amd64/arm64 架构")
            return False

        client = CLIENTS[mode]
        PrintUtils.print_info("当前架构: {}".format(osarch))
        PrintUtils.print_info("准备安装: {} {}".format(client["name"], client["tag"]))
        if not self._install_deb_package(client):
            PrintUtils.print_error("安装失败，请检查网络、系统软件源或依赖修复状态")
            return False

        PrintUtils.print_success("{} 安装完成".format(client["name"]))

        subscribe_url = self._read_input_subscription()
        if subscribe_url:
            self._auto_import_subscription(subscribe_url)
        else:
            PrintUtils.print_warn(
                "未输入订阅地址，可稍后在客户端导入，推荐: {}".format(
                    self.RECOMMEND_SUBSCRIBE_URL
                )
            )

        user_homes = FileUtils.getusershome()
        if len(user_homes) > 0:
            self._setup_proxy_alias(user_homes[0], client["port"])
        else:
            PrintUtils.print_warn("未找到用户目录，跳过 proxy_add 快捷命令写入")

        self._print_launch_tips(client)
        return True

    def run(self):
        return self.install_proxy_tool()
