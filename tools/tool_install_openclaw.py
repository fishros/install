# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, AptUtils, osversion
from .tool_install_nodejs import Tool as NodejsTool


class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装OpenClaw智能AI助手"
        self.type = BaseTool.TYPE_INSTALL
        self.author = "小鱼"

    def _run_cmd(self, cmd, timeout=0, msg=None):
        if msg:
            PrintUtils.print_info(msg)
        result = CmdTask(cmd, timeout).run()
        return result

    def _code(self, result):
        if isinstance(result, tuple) and len(result) > 0:
            return result[0]
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return -1

    def _out_lines(self, result):
        if (
            isinstance(result, tuple)
            and len(result) > 1
            and isinstance(result[1], list)
        ):
            return result[1]
        return []

    def _install_base_deps(self):
        if not AptUtils.checkapt():
            PrintUtils.print_error("apt更新失败，无法继续安装OpenClaw")
            return False
        dep_cmd = "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates curl wget git jq"
        result = self._run_cmd(dep_cmd, 300, "安装OpenClaw依赖中...")
        if self._code(result) != 0:
            PrintUtils.print_error("依赖安装失败，请检查apt源或网络")
            return False
        return True

    def _ensure_nodejs(self):
        check_result = self._run_cmd("node -v", 10, "检查Node.js版本...")
        node_out = self._out_lines(check_result)
        has_npm = self._code(self._run_cmd("npm -v", 10, "检查npm版本...")) == 0
        has_sudo_npm = (
            self._code(self._run_cmd("sudo npm -v", 10, "检查sudo环境npm...")) == 0
        )

        if (
            self._code(check_result) == 0
            and len(node_out) > 0
            and has_npm
            and has_sudo_npm
        ):
            node_ver = str(node_out[0]).strip().lower().replace("v", "")
            major_str = node_ver.split(".")[0]
            if major_str.isdigit() and int(major_str) >= 22:
                PrintUtils.print_success(
                    "检测到Node.js版本满足要求:{}".format(node_ver)
                )
                return True

        if self._code(check_result) == 0 and len(node_out) > 0:
            node_ver = str(node_out[0]).strip().lower().replace("v", "")
            PrintUtils.print_warn(
                "检测到Node.js环境不满足OpenClaw要求: {}".format(node_ver)
            )
        else:
            PrintUtils.print_warn("检测到Node.js未安装或不可用")

        PrintUtils.print_info("将自动安装默认Node.js 22版本...")
        return NodejsTool().install_nodejs_version(22, with_registry=False)

    def _init_env_file(self, user):
        if user == "root":
            home = "/root"
            sudo_prefix = ""
        else:
            home = "/home/{}".format(user)
            sudo_prefix = "sudo -u {} ".format(user)

        openclaw_dir = "{}/.openclaw".format(home)
        env_file = "{}/env".format(openclaw_dir)
        bashrc = "{}/.bashrc".format(home)

        self._run_cmd(
            "{}mkdir -p {}/agents/main/sessions {}/agents/main/agent {}/credentials".format(
                sudo_prefix, openclaw_dir, openclaw_dir, openclaw_dir
            ),
            30,
        )
        self._run_cmd("{}chmod 700 {}".format(sudo_prefix, openclaw_dir), 10)

        exists_result = self._run_cmd("test -f {}".format(env_file), 5)
        if self._code(exists_result) != 0:
            self._run_cmd("{}touch {}".format(sudo_prefix, env_file), 5)
            self._run_cmd("{}chmod 600 {}".format(sudo_prefix, env_file), 5)

        FileUtils.find_replace_sub(
            bashrc, "# >>> openclaw env >>>", "# <<< openclaw env <<<", ""
        )
        FileUtils.append(
            bashrc,
            '# >>> openclaw env >>>\n[ -f "{}" ] && source "{}"\n# <<< openclaw env <<<'.format(
                env_file, env_file
            ),
        )
        PrintUtils.print_success("已完成用户{}的OpenClaw环境初始化".format(user))

    def install_openclaw(self):
        os_name = str(osversion.get_name()).lower()
        if os_name not in ["ubuntu", "debian"]:
            PrintUtils.print_warn(
                "当前系统为{}，仅保证Ubuntu/Debian安装流程可用".format(os_name)
            )

        PrintUtils.print_info(
            "开始安装OpenClaw，流程将参考OpenClawInstaller并在本地执行"
        )
        if not self._install_base_deps():
            return False

        if not self._ensure_nodejs():
            return False

        npm_result = self._run_cmd(
            "sudo npm install -g openclaw@latest --unsafe-perm",
            0,
            "安装OpenClaw主程序中...",
        )
        if self._code(npm_result) != 0:
            PrintUtils.print_error("OpenClaw安装失败，请检查npm日志")
            return False

        prefix_result = self._run_cmd(
            "sudo npm prefix -g", 10, "定位OpenClaw安装目录..."
        )
        if self._code(prefix_result) == 0 and len(self._out_lines(prefix_result)) > 0:
            npm_prefix = str(self._out_lines(prefix_result)[0]).strip()
            self._run_cmd(
                "sudo ln -sf {}/bin/openclaw /usr/local/bin/openclaw".format(
                    npm_prefix
                ),
                10,
                "写入openclaw命令到系统PATH...",
            )
            self._run_cmd(
                "sudo test -x {}/bin/openclaw || sudo ln -sf {}/lib/node_modules/openclaw/openclaw.mjs /usr/local/bin/openclaw".format(
                    npm_prefix, npm_prefix
                ),
                10,
                "修复openclaw命令链接...",
            )

        version_result = self._run_cmd("openclaw --version", 10)
        if self._code(version_result) != 0:
            version_result = self._run_cmd("/usr/local/bin/openclaw --version", 10)
        if self._code(version_result) != 0:
            PrintUtils.print_error("OpenClaw命令不可用，请检查/usr/local/bin/openclaw")
            return False

        users = FileUtils.getusers()
        if len(users) > 0:
            self._init_env_file(users[0])

        self._run_cmd(
            "openclaw config set gateway.mode local", 20, "初始化OpenClaw网关模式..."
        )

        PrintUtils.print_success("OpenClaw安装完成")
        PrintUtils.print_info("可执行: openclaw onboard")
        PrintUtils.print_info("启动网关: openclaw gateway start")
        return True

    def run(self):
        self.install_openclaw()
