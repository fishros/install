# -*- coding: utf-8 -*-
import os

from .base import BaseTool
from .base import PrintUtils, CmdTask, ChooseTask
from .tool_install_nodejs import Tool as NodejsTool


class Tool(BaseTool):
    NPM_MIRROR = "https://registry.npmmirror.com"
    NPM_TAOBAO = "https://registry.npm.taobao.org"
    PREFERRED_NRM_ALIASES = ["taobao", "tencent", "huawei", "npm", "yarn", "cnpm"]

    def __init__(self):
        self.name = "一键安装OpenCode"
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

    def _remove_local_opencode(self):
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
        if registry_ready:
            install_cmds = [
                (
                    "sudo npm i -g opencode-ai",
                    "安装OpenCode中(使用已切换的npm源)...",
                ),
                (
                    "sudo npm i -g opencode-ai --registry={}".format(self.NPM_MIRROR),
                    "当前npm源安装失败，使用国内镜像参数重试...",
                ),
            ]
        else:
            install_cmds = [
                (
                    "sudo npm i -g opencode-ai --registry={}".format(self.NPM_MIRROR),
                    "安装OpenCode中(优先使用国内npm镜像)...",
                ),
                (
                    "sudo npm i -g opencode-ai",
                    "国内npm镜像安装失败，回退官方源重试...",
                ),
            ]

        for cmd, msg in install_cmds:
            result = self._run_cmd(cmd, 300, msg)
            if self._code(result) == 0:
                return True
            if self._has_text(result, "ENOTEMPTY"):
                PrintUtils.print_warn("检测到旧版OpenCode残留目录，开始自动清理后重试")
                if self._cleanup_global_opencode():
                    retry_result = self._run_cmd(cmd, 300, "重新安装OpenCode中...")
                    if self._code(retry_result) == 0:
                        return True
        return False

    def _cleanup_global_opencode(self):
        prefix_result = self._run_cmd("sudo npm prefix -g", 10, "定位npm全局目录...")
        prefix_out = self._out(prefix_result)
        if self._code(prefix_result) != 0 or len(prefix_out) == 0:
            PrintUtils.print_warn("未能定位npm全局目录，无法自动清理残留")
            return False

        npm_prefix = str(prefix_out[0]).strip()
        module_root = "{}/lib/node_modules".format(npm_prefix)
        cleanup_cmd = (
            "sudo rm -rf "
            "{root}/opencode-ai "
            "{root}/.opencode-ai-* "
            "/usr/local/bin/opencode"
        ).format(root=module_root)
        cleanup_result = self._run_cmd(
            cleanup_cmd,
            30,
            "清理OpenCode全局残留目录...",
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
        if "taobao" in sources:
            taobao_url = sources["taobao"]

        PrintUtils.print_info("自动切换npm源: 先taobao，失败回退npmmirror")

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
            self._run_cmd("npm config get registry", 10, "当前npm源:")
            PrintUtils.print_success("npm源已切换为taobao")
            return True

        PrintUtils.print_warn("taobao源不可用，回退到npmmirror")
        mirror_ready = node_tool._set_registry(self.NPM_MIRROR)
        if not mirror_ready:
            return False

        if self._check_registry_available("npmmirror"):
            self._run_cmd("npm config get registry", 10, "当前npm源:")
            PrintUtils.print_success("npm源已切换为npmmirror")
            return True

        PrintUtils.print_warn("npmmirror连通性检测失败，将继续尝试安装")
        self._run_cmd("npm config get registry", 10, "当前npm源:")
        return False

    def _ensure_nodejs(self):
        check_node = self._run_cmd("node -v", 10, "检查Node.js版本...")
        check_npm = self._run_cmd("npm -v", 10, "检查npm版本...")
        check_sudo_npm = self._run_cmd("sudo npm -v", 10, "检查sudo环境npm...")
        if (
            self._code(check_node) == 0
            and self._code(check_npm) == 0
            and self._code(check_sudo_npm) == 0
        ):
            return True
        PrintUtils.print_warn("检测到Node.js/npm环境不完整，将自动安装Node.js 22")
        return NodejsTool().install_nodejs_version(22, with_registry=False)

    def install_opencode(self):
        if not self._ensure_nodejs():
            PrintUtils.print_error("Node.js环境准备失败，无法安装OpenCode")
            return False

        registry_ready = self._switch_npm_registry()
        if not registry_ready:
            PrintUtils.print_warn("npm源切换失败，将直接使用镜像参数继续安装")

        if not self._install_with_registry_fallback(registry_ready):
            PrintUtils.print_error("OpenCode安装失败，请检查npm网络、镜像可用性和权限")
            return False

        prefix_result = self._run_cmd(
            "sudo npm prefix -g", 10, "定位OpenCode安装目录..."
        )
        prefix_out = self._out(prefix_result)
        if self._code(prefix_result) == 0 and len(prefix_out) > 0:
            npm_prefix = str(prefix_out[0]).strip()
            self._run_cmd(
                "sudo ln -sf {}/bin/opencode /usr/local/bin/opencode".format(
                    npm_prefix
                ),
                10,
                "写入opencode命令到系统PATH...",
            )

        verify = self._run_cmd("opencode --version", 10, "验证OpenCode版本...")
        if self._code(verify) != 0:
            verify = self._run_cmd(
                "sudo npm list -g opencode-ai --depth=0",
                20,
                "验证OpenCode安装状态...",
            )
            if self._code(verify) != 0:
                PrintUtils.print_error("OpenCode验证失败，请重新执行安装")
                return False

        PrintUtils.print_success("OpenCode安装完成")
        PrintUtils.print_info("可通过命令 opencode 启动")
        PrintUtils.print_info("可通过命令 opencode web 打开网页使用")
        return True

    def uninstall_opencode(self):
        self._run_cmd(
            "sudo rm -f /usr/local/bin/opencode", 10, "清理opencode命令链接..."
        )
        local_removed = self._remove_local_opencode()

        npm_installed = self._run_cmd(
            "sudo npm list -g opencode-ai --depth=0",
            20,
            "检查npm全局OpenCode安装...",
        )
        if self._code(npm_installed) == 0:
            uninstall_result = self._run_cmd(
                "sudo npm uninstall -g opencode-ai",
                120,
                "卸载OpenCode中...",
            )
            if self._code(uninstall_result) != 0:
                PrintUtils.print_error("npm全局OpenCode卸载失败，请检查npm权限或网络")
                return False
        else:
            PrintUtils.print_info("未检测到npm全局安装的OpenCode，跳过npm卸载")

        verify = self._run_cmd("opencode --version", 10, "验证OpenCode是否已卸载...")
        if self._code(verify) == 0:
            PrintUtils.print_warn(
                "检测到opencode命令仍存在，请检查PATH中的其他安装位置"
            )
            return False

        if not local_removed:
            return False

        PrintUtils.print_success("OpenCode卸载完成")
        return True

    def run(self):
        action_dic = {
            1: "安装OpenCode",
            2: "卸载OpenCode",
        }
        code, _ = ChooseTask(action_dic, "请选择操作:", False).run()
        if code == 1:
            self.install_opencode()
        elif code == 2:
            self.uninstall_opencode()
        else:
            PrintUtils.print_warn("已取消OpenCode操作")
