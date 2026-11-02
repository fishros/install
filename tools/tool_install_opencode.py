# -*- coding: utf-8 -*-
# 菜单 [18]: 一键安装/卸载 AI 编程工具. 原来只装 OpenCode, 文件名沿用(菜单的工具路径是对外接口, 不改名)
import os
import re

from .base import BaseTool
from .base import PrintUtils, CmdTask, ChooseTask, DownloadUtils
from .base import osarch
from .tool_install_nodejs import Tool as NodejsTool

# npm 安装的命令行工具. node 是需要的最低 Node.js 版本(取自各包 package.json 的 engines, 没写的按 20 算)
NPM_APPS = {
    1: {"name": "OpenCode", "tip": "OpenCode: 开源AI编程助手(命令行/网页)",
        "pkg": "opencode-ai", "bin": "opencode", "node": (20, 0),
        "usage": ["启动: opencode", "网页版: opencode web"]},
    2: {"name": "Codex", "tip": "Codex: OpenAI 的命令行编程助手",
        "pkg": "@openai/codex", "bin": "codex", "node": (16, 0),
        "usage": ["启动: codex (首次使用按提示登录 OpenAI 账号或配置 API Key)"]},
    3: {"name": "Claude Code", "tip": "Claude Code: Anthropic 的命令行编程助手",
        "pkg": "@anthropic-ai/claude-code", "bin": "claude", "node": (22, 0),
        "usage": ["启动: claude (需要 Anthropic 账号, 或用 CC Switch 切换到其它兼容的模型供应商)"]},
    4: {"name": "DeepSeek Harness", "tip": "DeepSeek Harness(dsh): DeepSeek 官方的智能体框架(预览版)",
        "pkg": "@deepseek-ai/dsh", "bin": "dsh", "node": (20, 0),
        "usage": ["网页版: dsh web (启动后在浏览器打开它打印的 http://127.0.0.1:3080/?token=... 地址)",
                  "查看用法: dsh --help", "目前是预览版, 用法可能会变"]},
    5: {"name": "Pi", "tip": "Pi: 极简、可扩展的命令行编程助手",
        "pkg": "@earendil-works/pi-coding-agent", "bin": "pi", "node": (22, 19),
        "usage": ["启动: pi"]},
}
# 从 GitHub Releases 下载 deb 安装的图形界面工具. tag 是自动获取最新版失败时用的版本;
# file 里的 {tag} 是带 v 的版本号, {ver} 是不带 v 的; arch 是系统架构到安装包命名的对应
DEB_APPS = {
    6: {"name": "CC Switch", "tip": "CC Switch: 图形界面, 一键切换 Claude Code/Codex 等工具的模型供应商",
        "repo": "farion1231/cc-switch", "tag": "v4.0.24", "deb": "cc-switch",
        "file": "CC-Switch-{tag}-Linux-{arch}.deb", "arch": {"amd64": "x86_64", "arm64": "arm64"},
        "usage": ["启动: 在应用菜单中搜索 CC Switch"]},
    7: {"name": "Cockpit Tools", "tip": "Cockpit Tools: 图形界面, 管理多个AI编程工具的账号和额度",
        "repo": "jlcodes99/cockpit-tools", "tag": "v1.3.78", "deb": "cockpit-tools",
        "file": "Cockpit.Tools_{ver}_{arch}.deb", "arch": {"amd64": "amd64", "arm64": "arm64"},
        "usage": ["启动: 在应用菜单中搜索 Cockpit Tools"]},
}


class Tool(BaseTool):
    NPM_MIRROR = "https://registry.npmmirror.com"
    # 淘宝源早已迁到 npmmirror, 旧域名 registry.npm.taobao.org 2024 年起停用, 连不上只会白白多试一次
    NPM_TAOBAO = "https://registry.npmmirror.com"
    PREFERRED_NRM_ALIASES = ["taobao", "tencent", "huawei", "npm", "yarn", "cnpm"]

    def __init__(self):
        self.name = "一键安装AI编程工具"
        self.type = BaseTool.TYPE_INSTALL
        self.author = "小鱼"
        self.app = NPM_APPS[1]

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

    def _err(self, result):
        if (
            isinstance(result, tuple)
            and len(result) > 2
            and isinstance(result[2], list)
        ):
            return result[2]
        return []

    def _has_text(self, result, keyword):
        keyword = str(keyword).lower()
        for line in self._out(result) + self._err(result):
            if keyword in str(line).lower():
                return True
        return False

    def _check_registry_available(self, name):
        ping_result = self._run_cmd("npm ping", 20, "测试{}连通性...".format(name))
        return self._code(ping_result) == 0

    def _print_runtime_diagnostics(self):
        self._run_cmd("npm prefix -g", 10, "当前用户npm全局目录:")
        self._run_cmd("sudo npm prefix -g", 10, "sudo环境npm全局目录:")
        self._run_cmd("which npm", 10, "npm路径:")
        self._run_cmd("which node", 10, "node路径:")

    def _fix_npm_prefix(self):
        prefix_result = self._run_cmd("sudo npm prefix -g", 10, "检查npm全局目录...")
        prefix_out = self._out(prefix_result)
        if self._code(prefix_result) != 0 or len(prefix_out) == 0:
            PrintUtils.print_warn("未能读取sudo环境npm全局目录")
            return False

        prefix = str(prefix_out[0]).strip()
        if not prefix.startswith("/root"):
            return True

        PrintUtils.print_warn("检测到npm全局目录位于/root，开始修复为/usr/local")
        self._run_cmd("sudo npm config delete prefix", 10, "清理错误npm prefix配置...")
        set_result = self._run_cmd(
            "sudo npm config set prefix /usr/local",
            10,
            "设置npm全局目录为/usr/local...",
        )
        if self._code(set_result) != 0:
            return False

        verify = self._run_cmd("sudo npm prefix -g", 10, "校验修复后的npm全局目录...")
        verify_out = self._out(verify)
        if self._code(verify) != 0 or len(verify_out) == 0:
            return False
        fixed_prefix = str(verify_out[0]).strip()
        if fixed_prefix.startswith("/root"):
            PrintUtils.print_warn("npm全局目录仍在/root，请手动检查 /root/.npmrc")
            return False
        return True

    def _cleanup_bad_link(self):
        link = "/usr/local/bin/{}".format(self.app["bin"])
        target_result = self._run_cmd("readlink -f {}".format(link), 10)
        if self._code(target_result) != 0 or len(self._out(target_result)) == 0:
            return True
        target = str(self._out(target_result)[0]).strip()
        if target.startswith("/root/"):
            PrintUtils.print_warn("检测到{}链接指向/root，清理旧链接...".format(self.app["bin"]))
            rm_result = self._run_cmd("sudo rm -f {}".format(link), 10)
            return self._code(rm_result) == 0
        return True

    def _ensure_command(self):
        cmd = self.app["bin"]
        user_check = self._run_cmd("command -v {}".format(cmd), 10)
        if self._code(user_check) == 0:
            return True

        prefix_result = self._run_cmd(
            "sudo npm prefix -g", 10, "定位{}安装目录...".format(self.app["name"])
        )
        prefix_out = self._out(prefix_result)
        if self._code(prefix_result) != 0 or len(prefix_out) == 0:
            return False

        npm_prefix = str(prefix_out[0]).strip()
        if npm_prefix.startswith("/root"):
            PrintUtils.print_warn("{}安装目录位于/root，普通用户可能无法访问".format(self.app["name"]))
            return False

        link_result = self._run_cmd(
            "sudo ln -sf {}/bin/{} /usr/local/bin/{}".format(npm_prefix, cmd, cmd),
            10,
            "写入{}命令到系统PATH...".format(cmd),
        )
        if self._code(link_result) != 0:
            return False

        verify = self._run_cmd("command -v {}".format(cmd), 10)
        return self._code(verify) == 0

    def _remove_local_opencode(self):
        # 只有 OpenCode 有官方脚本装到 ~/.opencode 的情况
        if self.app["pkg"] != "opencode-ai":
            return True
        local_dir = os.path.expanduser("~/.opencode")
        local_bin = os.path.join(local_dir, "bin", "opencode")
        if not os.path.exists(local_bin):
            return True

        remove_result = self._run_cmd(
            'rm -rf "{}"'.format(local_dir),
            30,
            "清理用户目录中的OpenCode安装...",
        )
        if self._code(remove_result) != 0:
            PrintUtils.print_warn(
                "用户目录中的OpenCode清理失败，请手动检查 {}".format(local_dir)
            )
            return False
        return True

    def _install_with_registry_fallback(self, registry_ready):
        pkg, name = self.app["pkg"], self.app["name"]
        if registry_ready:
            install_cmds = [
                (
                    "sudo npm i -g {}".format(pkg),
                    "安装{}中(使用已切换的npm源)...".format(name),
                ),
                (
                    "sudo npm i -g {} --registry={}".format(pkg, self.NPM_MIRROR),
                    "当前npm源安装失败，使用国内镜像参数重试...",
                ),
            ]
        else:
            install_cmds = [
                (
                    "sudo npm i -g {} --registry={}".format(pkg, self.NPM_MIRROR),
                    "安装{}中(优先使用国内npm镜像)...".format(name),
                ),
                (
                    "sudo npm i -g {}".format(pkg),
                    "国内npm镜像安装失败，回退官方源重试...",
                ),
            ]

        for cmd, msg in install_cmds:
            result = self._run_cmd(cmd, 300, msg)
            if self._code(result) == 0:
                return True
            if self._has_text(result, "ENOTEMPTY"):
                PrintUtils.print_warn("检测到旧版{}残留目录，开始自动清理后重试".format(name))
                if self._cleanup_global_install():
                    retry_result = self._run_cmd(cmd, 300, "重新安装{}中...".format(name))
                    if self._code(retry_result) == 0:
                        return True
        return False

    def _cleanup_global_install(self):
        prefix_result = self._run_cmd("sudo npm prefix -g", 10, "定位npm全局目录...")
        prefix_out = self._out(prefix_result)
        if self._code(prefix_result) != 0 or len(prefix_out) == 0:
            PrintUtils.print_warn("未能定位npm全局目录，无法自动清理残留")
            return False

        npm_prefix = str(prefix_out[0]).strip()
        module_root = "{}/lib/node_modules".format(npm_prefix)
        # npm 升级中断会留下「.包名-随机串」临时目录; 带 scope 的包(@openai/codex)临时目录在 scope 目录里
        pkg = self.app["pkg"]
        scope, _, base = pkg.rpartition("/")
        if scope:
            tmp_dir = "{}/{}/.{}-*".format(module_root, scope, base)
        else:
            tmp_dir = "{}/.{}-*".format(module_root, base)
        cleanup_cmd = "sudo rm -rf {root}/{pkg} {tmp} /usr/local/bin/{bin}".format(
            root=module_root, pkg=pkg, tmp=tmp_dir, bin=self.app["bin"])
        cleanup_result = self._run_cmd(
            cleanup_cmd,
            30,
            "清理{}全局残留目录...".format(self.app["name"]),
        )
        return self._code(cleanup_result) == 0

    def _switch_npm_registry(self):
        node_tool = NodejsTool()
        node_tool._run_cmd = self._run_cmd

        nrm_check = self._run_cmd(
            "/usr/local/bin/nrm --version", 10, "检查nrm是否可用..."
        )
        if self._code(nrm_check) != 0:
            PrintUtils.print_info("未检测到nrm，先安装nrm并切换npm源...")
            install_result = self._run_cmd(
                "sudo npm install -g nrm", 180, "安装nrm中..."
            )
            if self._code(install_result) != 0:
                return False

            prefix_result = self._run_cmd("sudo npm prefix -g", 10)
            prefix_out = self._out(prefix_result)
            if self._code(prefix_result) == 0 and len(prefix_out) > 0:
                npm_prefix = str(prefix_out[0]).strip()
                self._run_cmd(
                    "sudo ln -sf {}/bin/nrm /usr/local/bin/nrm".format(npm_prefix),
                    10,
                    "写入nrm命令到系统PATH...",
                )

        sources = node_tool._get_nrm_sources()
        taobao_url = self.NPM_TAOBAO
        if "taobao" in sources and str(sources["taobao"]).strip().rstrip("/") != taobao_url:
            PrintUtils.print_warn(
                "检测到nrm中的taobao源为{}，将优先使用固定taobao地址{}".format(
                    sources["taobao"], taobao_url
                )
            )

        PrintUtils.print_info(
            "自动切换npm源: 先tencent，失败再试taobao，最后回退npmmirror"
        )

        if "tencent" in sources:
            PrintUtils.print_info("先尝试切换到tencent源并检测连通性...")
            tencent_result = self._run_cmd("/usr/local/bin/nrm use tencent", 20)
            tencent_ok = False
            if self._code(tencent_result) == 0 and (
                not node_tool._has_error_text(tencent_result)
            ):
                tencent_url = str(sources["tencent"]).strip()
                if node_tool._set_registry(
                    tencent_url
                ) and self._check_registry_available("tencent"):
                    current_registry = self._run_cmd(
                        "npm config get registry", 10, "当前npm源:"
                    )
                    registry_out = self._out(current_registry)
                    if len(registry_out) > 0:
                        PrintUtils.print_success(
                            "npm源已切换为 tencent -> {}".format(registry_out[0])
                        )
                    else:
                        PrintUtils.print_success("npm源已切换为 tencent")
                    tencent_ok = True
            if tencent_ok:
                return True
            PrintUtils.print_warn("tencent源不可用，继续尝试taobao")

        taobao_ready = False
        if "taobao" in sources:
            result = self._run_cmd("/usr/local/bin/nrm use taobao", 20)
            if self._code(result) == 0 and (not node_tool._has_error_text(result)):
                taobao_ready = node_tool._set_registry(taobao_url)
            else:
                PrintUtils.print_warn("nrm切换taobao失败，尝试直接写入taobao配置")
                taobao_ready = node_tool._set_registry(taobao_url)
        else:
            PrintUtils.print_warn("nrm源中未找到taobao，尝试直接写入taobao配置")
            taobao_ready = node_tool._set_registry(taobao_url)

        if taobao_ready and self._check_registry_available("taobao"):
            current_registry = self._run_cmd(
                "npm config get registry", 10, "当前npm源:"
            )
            registry_out = self._out(current_registry)
            if len(registry_out) > 0:
                PrintUtils.print_success(
                    "npm源已切换为 taobao -> {}".format(registry_out[0])
                )
            else:
                PrintUtils.print_success("npm源已切换为 taobao")
            return True

        PrintUtils.print_warn("taobao源不可用，回退到npmmirror")
        mirror_ready = node_tool._set_registry(self.NPM_MIRROR)
        if not mirror_ready:
            return False

        if self._check_registry_available("npmmirror"):
            current_registry = self._run_cmd(
                "npm config get registry", 10, "当前npm源:"
            )
            registry_out = self._out(current_registry)
            if len(registry_out) > 0:
                PrintUtils.print_success(
                    "npm源已切换为 npmmirror -> {}".format(registry_out[0])
                )
            else:
                PrintUtils.print_success("npm源已切换为 npmmirror")
            return True

        PrintUtils.print_warn("npmmirror连通性检测失败，将继续尝试安装")
        self._run_cmd("npm config get registry", 10, "当前npm源:")
        return False

    def _node_version(self):
        result = self._run_cmd("node -v", 10, "检查Node.js版本...")
        match = re.match(r"v(\d+)\.(\d+)", " ".join(self._out(result)).strip())
        if self._code(result) != 0 or not match:
            return None
        return int(match.group(1)), int(match.group(2))

    def _ensure_nodejs(self):
        need = self.app["node"]
        version = self._node_version()
        check_npm = self._run_cmd("npm -v", 10, "检查npm版本...")
        check_sudo_npm = self._run_cmd("sudo npm -v", 10, "检查sudo环境npm...")
        if (
            version is not None
            and self._code(check_npm) == 0
            and self._code(check_sudo_npm) == 0
        ):
            if version >= need:
                return True
            PrintUtils.print_warn("{}需要Node.js {}.{}以上, 当前是 {}.{}, 将自动安装Node.js 24".format(
                self.app["name"], need[0], need[1], version[0], version[1]))
        else:
            PrintUtils.print_warn("检测到Node.js/npm环境不完整，将自动安装Node.js 24")
        return NodejsTool().install_nodejs_version(24, with_registry=False)

    def install_npm_app(self):
        name, cmd = self.app["name"], self.app["bin"]
        if not self._ensure_nodejs():
            PrintUtils.print_error("Node.js环境准备失败，无法安装{}".format(name))
            return False

        if not self._fix_npm_prefix():
            PrintUtils.print_warn("npm全局目录修复失败，安装可能受影响")
        if not self._cleanup_bad_link():
            PrintUtils.print_warn("旧版{}命令链接清理失败".format(cmd))

        self._print_runtime_diagnostics()

        registry_ready = self._switch_npm_registry()
        if not registry_ready:
            PrintUtils.print_warn("npm源切换失败，将直接使用镜像参数继续安装")

        if not self._install_with_registry_fallback(registry_ready):
            PrintUtils.print_error("{}安装失败，请检查npm网络、镜像可用性和权限".format(name))
            return False

        if not self._ensure_command():
            PrintUtils.print_warn("未能自动修复{}命令路径，将继续进行安装校验".format(cmd))

        verify = self._run_cmd("{} --version".format(cmd), 10, "验证{}版本...".format(name))
        if self._code(verify) != 0:
            verify = self._run_cmd(
                "sudo npm list -g {} --depth=0".format(self.app["pkg"]),
                20,
                "验证{}安装状态...".format(name),
            )
            if self._code(verify) != 0:
                PrintUtils.print_error("{}验证失败，请重新执行安装".format(name))
                return False

        PrintUtils.print_success("{}安装完成".format(name))
        for line in self.app["usage"]:
            PrintUtils.print_info(line)
        return True

    def uninstall_npm_app(self):
        name, cmd, pkg = self.app["name"], self.app["bin"], self.app["pkg"]
        self._run_cmd(
            "sudo rm -f /usr/local/bin/{}".format(cmd), 10, "清理{}命令链接...".format(cmd)
        )
        local_removed = self._remove_local_opencode()

        npm_installed = self._run_cmd(
            "sudo npm list -g {} --depth=0".format(pkg),
            20,
            "检查npm全局{}安装...".format(name),
        )
        if self._code(npm_installed) == 0:
            uninstall_result = self._run_cmd(
                "sudo npm uninstall -g {}".format(pkg),
                120,
                "卸载{}中...".format(name),
            )
            if self._code(uninstall_result) != 0:
                PrintUtils.print_error("npm全局{}卸载失败，请检查npm权限或网络".format(name))
                return False
        else:
            PrintUtils.print_info("未检测到npm全局安装的{}，跳过npm卸载".format(name))

        verify = self._run_cmd("command -v {}".format(cmd), 10, "验证{}是否已卸载...".format(name))
        if self._code(verify) == 0:
            PrintUtils.print_warn(
                "检测到{}命令仍存在，请检查PATH中的其他安装位置".format(cmd)
            )
            return False

        if not local_removed:
            return False

        PrintUtils.print_success("{}卸载完成".format(name))
        return True

    def _deb_installed(self, pkg):
        result = self._run_cmd("dpkg-query -W -f='${Status}' " + pkg, 10)
        return "install ok installed" in " ".join(self._out(result))

    def install_deb_app(self):
        app = self.app
        if osarch not in app["arch"]:
            PrintUtils.print_error("{}暂不支持当前系统架构:{}".format(app["name"], osarch))
            return False
        PrintUtils.print_info("正在获取{}最新版本...".format(app["name"]))
        tag = DownloadUtils.github_latest_tag(app["repo"])
        if tag is None:
            tag = app["tag"]
            PrintUtils.print_warn("获取最新版本失败, 安装已知版本 {}".format(tag))
        file_name = app["file"].format(tag=tag, ver=tag.lstrip("v"), arch=app["arch"][osarch])
        PrintUtils.print_info("准备安装: {} {}".format(app["name"], tag))
        temp_file = "/tmp/fishros_ai_tool.deb"
        if not DownloadUtils.download_deb(DownloadUtils.github_sources(app["repo"], tag, file_name), temp_file):
            self._run_cmd('rm -f "{}"'.format(temp_file), 10)
            PrintUtils.print_error("{}下载失败，请检查网络后重试".format(app["name"]))
            return False
        # 用 apt 装本地包, 缺的依赖(webkit2gtk 等)会一起装上
        CmdTask('sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "{}"'.format(temp_file), 600, os_command=True).run()
        self._run_cmd('rm -f "{}"'.format(temp_file), 10)
        if not self._deb_installed(app["deb"]):
            PrintUtils.print_error("{}安装失败(Ubuntu 22.04以下的系统可能缺少依赖), 请把上面的报错信息发到鱼香社区求助".format(app["name"]))
            return False
        PrintUtils.print_success("{}安装完成".format(app["name"]))
        for line in app["usage"]:
            PrintUtils.print_info(line)
        return True

    def uninstall_deb_app(self):
        app = self.app
        if not self._deb_installed(app["deb"]):
            PrintUtils.print_info("未检测到已安装的{}".format(app["name"]))
            return True
        CmdTask("sudo DEBIAN_FRONTEND=noninteractive apt-get remove -y {}".format(app["deb"]), 300, os_command=True).run()
        if self._deb_installed(app["deb"]):
            PrintUtils.print_error("{}卸载失败".format(app["name"]))
            return False
        PrintUtils.print_success("{}卸载完成".format(app["name"]))
        return True

    def run(self):
        apps = dict(NPM_APPS)
        apps.update(DEB_APPS)
        while True:
            code, _ = ChooseTask({k: v["tip"] for k, v in apps.items()}, "请选择AI编程工具:", False).run()
            if code == 0:
                return BaseTool.BACK
            if code not in apps:
                continue
            self.app = apps[code]
            action, _ = ChooseTask({1: "安装" + self.app["name"], 2: "卸载" + self.app["name"]}, "请选择操作:", False).run()
            if action == 0:
                continue
            is_deb = code in DEB_APPS
            if action == 1:
                return self.install_deb_app() if is_deb else self.install_npm_app()
            return self.uninstall_deb_app() if is_deb else self.uninstall_npm_app()
