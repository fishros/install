# -*- coding: utf-8 -*-
import os
import re

from .base import BaseTool
from .base import PrintUtils, CmdTask, ChooseTask, FileUtils


class Tool(BaseTool):
    def __init__(self):
        self.name = "一键清理OpenClaw"
        self.type = BaseTool.TYPE_CONFIG
        self.author = "小鱼"

    def _run_cmd(self, cmd, timeout=0, msg=None):
        if msg:
            PrintUtils.print_info(msg)
        return CmdTask(cmd, timeout).run()

    def _code(self, result):
        if isinstance(result, tuple) and len(result) > 0:
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

    def _cleanup_openclaw_bin(self):
        self._run_cmd(
            "sudo rm -f /usr/local/bin/openclaw", 10, "清理openclaw命令链接..."
        )

        user_prefix = self._run_cmd("npm prefix -g", 10)
        user_prefix_out = self._out(user_prefix)
        if self._code(user_prefix) == 0 and len(user_prefix_out) > 0:
            prefix = str(user_prefix_out[0]).strip()
            self._run_cmd("rm -f {}/bin/openclaw".format(prefix), 10)

        root_prefix = self._run_cmd("sudo npm prefix -g", 10)
        root_prefix_out = self._out(root_prefix)
        if self._code(root_prefix) == 0 and len(root_prefix_out) > 0:
            prefix = str(root_prefix_out[0]).strip()
            self._run_cmd("sudo rm -f {}/bin/openclaw".format(prefix), 10)

    def _cleanup_openclaw_pkg(self):
        self._run_cmd("npm uninstall -g openclaw", 120, "卸载当前用户OpenClaw包...")
        self._run_cmd("sudo npm uninstall -g openclaw", 120, "卸载系统OpenClaw包...")

        user_root = self._run_cmd("npm root -g", 10)
        user_root_out = self._out(user_root)
        if self._code(user_root) == 0 and len(user_root_out) > 0:
            root = str(user_root_out[0]).strip()
            self._run_cmd("rm -rf {}/openclaw".format(root), 20)

        root_root = self._run_cmd("sudo npm root -g", 10)
        root_root_out = self._out(root_root)
        if self._code(root_root) == 0 and len(root_root_out) > 0:
            root = str(root_root_out[0]).strip()
            self._run_cmd("sudo rm -rf {}/openclaw".format(root), 20)

    def _cleanup_config(self, keep_config):
        if keep_config:
            PrintUtils.print_warn("已保留配置目录: ~/.openclaw")
            return
        self._run_cmd("rm -rf ~/.openclaw", 20, "清理当前用户OpenClaw配置...")
        self._run_cmd("sudo rm -rf /root/.openclaw", 20, "清理root用户OpenClaw配置...")

    def _cleanup_shell_init(self):
        bashrc_list = FileUtils.getbashrc()
        if "/root/.bashrc" not in bashrc_list:
            bashrc_list.append("/root/.bashrc")

        for bashrc in bashrc_list:
            if not os.path.exists(bashrc):
                continue
            try:
                with open(bashrc, "r", encoding="utf-8") as f:
                    content = f.read()

                content = re.sub(
                    r"\n?# >>> openclaw env >>>\n.*?\n# <<< openclaw env <<<\n?",
                    "\n",
                    content,
                    flags=re.S,
                )
                content = re.sub(
                    r"\n?# OpenClaw Completion\n\[ -f \".*?/\.openclaw/completions/openclaw\.bash\" \] && source \".*?/\.openclaw/completions/openclaw\.bash\"\n?",
                    "\n",
                    content,
                    flags=re.S,
                )
                content = re.sub(
                    r"\n?# OpenClaw Completion\nsource \".*?/\.openclaw/completions/openclaw\.bash\"\n?",
                    "\n",
                    content,
                    flags=re.S,
                )

                with open(bashrc, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception:
                pass

    def cleanup_openclaw(self):
        choose_dic = {
            1: "保留配置(~/.openclaw)",
            2: "完全清理(删除配置)",
        }
        code, _ = ChooseTask(choose_dic, "清理OpenClaw时是否保留配置:", False).run()
        if code == 0:
            PrintUtils.print_warn("已取消OpenClaw清理")
            return False

        keep_config = code == 1
        self._cleanup_openclaw_pkg()
        self._cleanup_openclaw_bin()
        self._cleanup_config(keep_config)
        self._cleanup_shell_init()

        verify = self._run_cmd("openclaw --version", 10, "验证OpenClaw是否已清理...")
        if self._code(verify) == 0:
            PrintUtils.print_warn("检测到openclaw命令仍存在，请检查PATH中其他安装位置")
            return False

        PrintUtils.print_success("OpenClaw清理完成")
        return True

    def run(self):
        self.cleanup_openclaw()
