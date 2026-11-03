# -*- coding: utf-8 -*-
import os
from urllib.parse import quote

from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, ChooseTask, DownloadUtils, AdUtils
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



class Tool(BaseTool):
    # 推荐的订阅注册链接在官网后台隐藏页 /admin/install/aff 里配置, 读不到官网时用这个默认值.
    # (原来指向论坛帖子 topic/668, 该帖 2024-10 已删除; 帖子里的 .au 注册地址国内也已连不上)
    DEFAULT_SUBSCRIBE_URL = "https://portal.shadowsocks.nz/aff.php?aff=41638"

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

    def _download_package(self, client, path):
        """GitHub 加速站在前, repo.trojan-cdn.com 兜底(一直能下, 但国内只有十几 KB/s)"""
        file_name = client["file"].format(arch=osarch)
        sources = DownloadUtils.github_sources(client["repo"], client["tag"], file_name)
        sources = [s for s in sources if s[0] != "GitHub 直连"]  # 直连基本下不动, 用 trojan-cdn 兜底
        sources.append(("trojan-cdn 镜像", "https://repo.trojan-cdn.com/{}/{}".format(client["cdn_dir"], file_name)))
        return DownloadUtils.download_deb(sources, path)

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

    def _recommend_url(self):
        return AdUtils.link("proxy_subscribe", self.DEFAULT_SUBSCRIBE_URL)

    def _read_input_subscription(self):
        recommend = self._recommend_url()
        if recommend:
            PrintUtils.print_warn("请输入订阅地址(若无请访问 {} 获取)".format(recommend))
        else:
            PrintUtils.print_warn("请输入订阅地址")
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
        elif self._recommend_url():
            PrintUtils.print_warn(
                "未输入订阅地址，可稍后在客户端导入，推荐: {}".format(self._recommend_url())
            )
        else:
            PrintUtils.print_warn("未输入订阅地址，可稍后在客户端导入")

        user_homes = FileUtils.getusershome()
        if len(user_homes) > 0:
            self._setup_proxy_alias(user_homes[0], client["port"])
        else:
            PrintUtils.print_warn("未找到用户目录，跳过 proxy_add 快捷命令写入")

        self._print_launch_tips(client)
        return True

    def run(self):
        return self.install_proxy_tool()
