# -*- coding: utf-8 -*-
import os
from urllib.parse import quote

from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, ChooseTask
from .base import osarch


class Tool(BaseTool):
    CLASH_VERGE_BASE = (
        "https://repo.trojan-cdn.com/clash-verge-rev/Clash%20Verge%20Rev%20v2.4.6"
    )
    MIHOMO_PARTY_BASE = "https://repo.trojan-cdn.com/mihomo-party/v1.9.2"
    RECOMMEND_SUBSCRIBE_URL = "https://fishros.org.cn/forum/topic/668"

    def __init__(self):
        self.name = "一键安装 Linux 代理科学上网工具"
        self.type = BaseTool.TYPE_INSTALL
        self.author = "小鱼"

    def _run_cmd(self, cmd, timeout=0, msg=None):
        if msg:
            PrintUtils.print_info(msg)
        return CmdTask(cmd, timeout, os_command=True).run()

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
        mode_dic = {
            1: "有界面版: Clash Verge Rev",
            2: "无界面版(按提供源): mihomo-party",
        }
        code, _ = ChooseTask(mode_dic, "请选择代理工具版本:", False).run()
        return code

    def _resolve_package(self, mode):
        if osarch not in ["amd64", "arm64"]:
            return None, None, None

        if mode == 1:
            filename_map = {
                "amd64": "Clash.Verge_2.4.6_amd64.deb",
                "arm64": "Clash.Verge_2.4.6_arm64.deb",
            }
            file_name = filename_map[osarch]
            return (
                "Clash Verge Rev",
                "{}/{}".format(self.CLASH_VERGE_BASE, file_name),
                file_name,
            )

        if mode == 2:
            filename_map = {
                "amd64": "mihomo-party-linux-1.9.2-amd64.deb",
                "arm64": "mihomo-party-linux-1.9.2-arm64.deb",
            }
            file_name = filename_map[osarch]
            return (
                "mihomo-party",
                "{}/{}".format(self.MIHOMO_PARTY_BASE, file_name),
                file_name,
            )

        return None, None, None

    def _install_deb_package(self, package_url):
        temp_file = "/tmp/fishros_proxy_tool.deb"
        download = self._run_cmd(
            'wget --no-proxy "{}" -O "{}"'.format(package_url, temp_file),
            300,
            "下载代理工具安装包中...",
        )
        if self._code(download) != 0:
            return False

        install = self._run_cmd(
            'sudo dpkg -i "{}"'.format(temp_file), 180, "安装代理工具中..."
        )
        if self._code(install) != 0:
            PrintUtils.print_warn("安装依赖不完整，尝试自动修复后重试...")
            fix_dep = self._run_cmd(
                "sudo DEBIAN_FRONTEND=noninteractive apt-get install -f -y",
                300,
                "修复依赖中...",
            )
            if self._code(fix_dep) != 0:
                self._run_cmd('rm -f "{}"'.format(temp_file), 10)
                return False
            install_retry = self._run_cmd(
                'sudo dpkg -i "{}"'.format(temp_file),
                180,
                "重新安装代理工具中...",
            )
            if self._code(install_retry) != 0:
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

    def _setup_proxy_alias(self, user_home):
        bashrc = os.path.join(user_home.rstrip("/"), ".bashrc")
        if not os.path.exists(bashrc):
            FileUtils.new(user_home.rstrip("/") + "/", name=".bashrc", data="")

        start_flag = "# >>> fishros proxy alias >>>"
        end_flag = "# <<< fishros proxy alias <<<"
        block = (
            "{}\n"
            "proxy_add(){\n"
            "  export http_proxy=http://127.0.0.1:7890\n"
            "  export https_proxy=http://127.0.0.1:7890\n"
            "  export all_proxy=socks5://127.0.0.1:7890\n"
            "  echo 'proxy on: 127.0.0.1:7890'\n"
            "}\n"
            "proxy_off(){\n"
            "  unset http_proxy https_proxy all_proxy\n"
            "  echo 'proxy off'\n"
            "}\n"
            "proxy_status(){\n"
            '  echo "http_proxy=$http_proxy"\n'
            '  echo "https_proxy=$https_proxy"\n'
            '  echo "all_proxy=$all_proxy"\n'
            "}\n"
            "{}"
        ).format(start_flag, end_flag)

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

        PrintUtils.print_success("已写入终端快捷命令: proxy_add/proxy_off/proxy_status")

    def _which(self, name):
        result = self._run_cmd("command -v {}".format(name), 10)
        if self._code(result) == 0 and len(self._out(result)) > 0:
            return str(self._out(result)[0]).strip()
        return None

    def _print_launch_tips(self, mode):
        PrintUtils.print_delay("==========使用方法===========")
        if mode == 1:
            cmd_path = self._which("clash-verge")
            if cmd_path is None:
                cmd_path = self._which("clash-verge-rev")
            if cmd_path:
                PrintUtils.print_delay("1.启动有界面客户端: {}".format(cmd_path))
            else:
                PrintUtils.print_delay(
                    "1.启动有界面客户端: 在应用菜单中搜索 Clash Verge"
                )
        else:
            cmd_path = self._which("mihomo-party")
            if cmd_path is None:
                cmd_path = self._which("clash-party")
            if cmd_path:
                PrintUtils.print_delay("1.启动工具: {}".format(cmd_path))
            else:
                PrintUtils.print_delay("1.启动工具: 在应用菜单中搜索 mihomo-party")

        PrintUtils.print_delay("2.开启终端代理: proxy_add")
        PrintUtils.print_delay("3.关闭终端代理: proxy_off")
        PrintUtils.print_delay("4.查看终端代理: proxy_status")
        PrintUtils.print_delay("5.若命令未生效，请执行: source ~/.bashrc")

    def install_proxy_tool(self):
        mode = self._choose_install_mode()
        if mode not in [1, 2]:
            PrintUtils.print_warn("已取消安装")
            return False

        package_name, package_url, file_name = self._resolve_package(mode)
        if package_name is None:
            PrintUtils.print_error("当前仅支持 amd64/arm64 架构")
            return False

        PrintUtils.print_info("当前架构: {}".format(osarch))
        PrintUtils.print_info("准备安装: {} ({})".format(package_name, file_name))
        if not self._install_deb_package(package_url):
            PrintUtils.print_error("安装失败，请检查网络或包是否可用")
            return False

        PrintUtils.print_success("{} 安装完成".format(package_name))

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
            self._setup_proxy_alias(user_homes[0])
        else:
            PrintUtils.print_warn("未找到用户目录，跳过 proxy_add 快捷命令写入")

        self._print_launch_tips(mode)
        return True

    def run(self):
        self.install_proxy_tool()
