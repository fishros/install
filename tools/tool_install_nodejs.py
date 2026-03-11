# -*- coding: utf-8 -*-
import os
import json
import re
import urllib.request

from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, AptUtils, ChooseTask


class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装nodejs并配置环境"
        self.type = BaseTool.TYPE_INSTALL
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

    def _detect_node_major(self):
        result = self._run_cmd("node -v", 10)
        if self._code(result) != 0:
            return None
        out = self._out(result)
        if len(out) == 0:
            return None
        ver = str(out[0]).strip().replace("v", "")
        major = ver.split(".")[0]
        if major.isdigit():
            return int(major)
        return None

    def _cleanup_legacy(self):
        self._run_cmd(
            "sudo rm -rf /opt/nodejs /tmp/nodejs.tar.xz", 10, "清理旧版Node.js残留..."
        )
        for bashrc in FileUtils.getbashrc():
            FileUtils.find_replace_sub(
                bashrc, "# >>> nodejs initialize >>>", "# <<< nodejs initialize <<<", ""
            )

    def _choose_target_major(self):
        version_dic = {
            1: "Node.js 22 LTS(默认推荐)",
            2: "Node.js 20 LTS",
            3: "Node.js 18 LTS(兼容)",
            4: "自定义主版本号",
        }
        code, _ = ChooseTask(version_dic, "请选择Node.js默认版本:", False).run()
        if code == 1:
            return 22
        if code == 2:
            return 20
        if code == 3:
            return 18
        if code == 4:
            custom = input("请输入Node.js主版本号(如22):").strip()
            if custom.isdigit() and int(custom) > 0:
                return int(custom)
            PrintUtils.print_warn("输入无效，默认使用22")
            return 22
        if os.environ.get("FISH_INSTALL_CONFIG") is not None:
            PrintUtils.print_warn("自动化模式未提供Node.js版本，默认使用22")
            return 22
        PrintUtils.print_warn("已取消Node.js安装")
        return None

    def _choose_registry(self, nrm_sources):
        if len(nrm_sources) == 0:
            return None, None

        aliases = list(nrm_sources.keys())
        preferred_order = ["taobao", "tencent", "huawei", "npm", "yarn", "cnpm"]
        sorted_aliases = []
        for alias in preferred_order:
            if alias in nrm_sources:
                sorted_aliases.append(alias)
        for alias in aliases:
            if alias not in sorted_aliases:
                sorted_aliases.append(alias)

        registry_dic = {}
        idx = 1
        alias_map = {}
        for alias in sorted_aliases:
            registry_dic[idx] = "{} -> {}".format(alias, nrm_sources[alias])
            alias_map[idx] = alias
            idx += 1
        skip_idx = idx
        registry_dic[skip_idx] = "跳过切换"

        code, _ = ChooseTask(registry_dic, "请选择npm源(基于nrm ls):", False).run()
        if code == skip_idx:
            return None, None
        if code in alias_map:
            alias = alias_map[code]
            return alias, nrm_sources[alias]

        if os.environ.get("FISH_INSTALL_CONFIG") is not None:
            default_alias = "taobao" if "taobao" in nrm_sources else sorted_aliases[0]
            PrintUtils.print_warn(
                "自动化模式未提供npm源，默认使用{}".format(default_alias)
            )
            return default_alias, nrm_sources[default_alias]
        return None, None

    def _set_registry(self, url):
        set_user = self._run_cmd("npm config set registry {}".format(url), 20)
        set_root = self._run_cmd("sudo npm config set registry {}".format(url), 20)
        return self._code(set_user) == 0 and self._code(set_root) == 0

    def _normalize_url(self, url):
        return str(url).strip().rstrip("/")

    def _has_error_text(self, result):
        for line in self._out(result):
            text = str(line).lower()
            if " error " in " {} ".format(text) or text.startswith("error"):
                return True
        return False

    def _get_nrm_sources(self):
        result = self._run_cmd("/usr/local/bin/nrm ls", 20, "读取nrm源列表...")
        if self._code(result) != 0:
            return {}
        sources = {}
        for line in self._out(result):
            text = re.sub(r"\x1b\[[0-9;]*m", "", str(line)).strip().replace("*", "")
            parts = text.split()
            if len(parts) >= 2 and parts[-1].startswith("http"):
                sources[parts[0].lower()] = parts[-1]
        return sources

    def _switch_registry(self):
        nrm_sources = self._get_nrm_sources()
        if len(nrm_sources) == 0:
            PrintUtils.print_error("未读取到可用nrm源，无法切换")
            return False

        alias, registry_url = self._choose_registry(nrm_sources)
        if alias is None or registry_url is None:
            PrintUtils.print_info("已跳过npm源切换")
            return True

        nrm_ok = False
        result = self._run_cmd("/usr/local/bin/nrm use {}".format(alias), 20)
        if self._code(result) == 0 and (not self._has_error_text(result)):
            nrm_ok = True

        if not nrm_ok:
            PrintUtils.print_warn("nrm切换失败，尝试直接写入npm源配置")

        if not self._set_registry(registry_url):
            PrintUtils.print_error("npm源切换失败")
            return False

        verify = self._run_cmd("npm config get registry", 10, "当前npm源:")
        if self._code(verify) != 0:
            return False
        PrintUtils.print_success("npm源已切换为{}".format(alias))
        return True

    def _install_nrm_and_registry(self):
        result = self._run_cmd("sudo npm install -g nrm", 180, "安装nrm中...")
        if self._code(result) != 0:
            PrintUtils.print_error("nrm安装失败")
            return False

        prefix_result = self._run_cmd("sudo npm prefix -g", 10)
        if self._code(prefix_result) == 0 and len(self._out(prefix_result)) > 0:
            npm_prefix = str(self._out(prefix_result)[0]).strip()
            self._run_cmd(
                "sudo ln -sf {}/bin/nrm /usr/local/bin/nrm".format(npm_prefix),
                10,
                "写入nrm命令到系统PATH...",
            )

        if self._code(self._run_cmd("/usr/local/bin/nrm --version", 10)) != 0:
            PrintUtils.print_error("nrm安装后校验失败")
            return False
        return self._switch_registry()

    def _post_node_setup(self, target_major, with_registry=True):
        self._run_cmd("node -v", 10, "Node.js版本:")
        self._run_cmd("npm -v", 10, "npm版本:")
        if not self._setup_user_npm_prefix():
            return False
        if with_registry:
            if not self._install_nrm_and_registry():
                return False
        PrintUtils.print_success("Node.js {} 安装并配置完成".format(target_major))
        return True

    def _fix_node_permissions(self):
        if self._code(self._run_cmd("test -d /opt/nodejs", 5)) != 0:
            return True

        self._run_cmd(
            "sudo chown -R root:root /opt/nodejs",
            30,
            "修正Node.js安装目录归属...",
        )
        self._run_cmd("sudo chmod -R a+rX /opt/nodejs", 30)
        self._run_cmd("sudo chmod -R go-w /opt/nodejs", 30)

        for bin_name in ["node", "npm", "npx", "nrm"]:
            self._run_cmd(
                "sudo test -e /usr/local/bin/{} && sudo chmod a+rx /usr/local/bin/{} || true".format(
                    bin_name, bin_name
                ),
                10,
            )

        return True

    def _setup_user_npm_prefix(self):
        user_home = os.path.expanduser("~")
        npm_global_dir = "{}/.npm-global".format(user_home)
        npm_global_bin = "{}/bin".format(npm_global_dir)
        bashrc = "{}/.bashrc".format(user_home)

        if (
            self._code(
                self._run_cmd(
                    "mkdir -p {}".format(npm_global_bin), 10, "初始化用户npm全局目录..."
                )
            )
            != 0
        ):
            PrintUtils.print_error("创建用户npm全局目录失败")
            return False

        if (
            self._code(
                self._run_cmd(
                    "npm config set prefix {}".format(npm_global_dir),
                    10,
                    "配置npm全局安装目录...",
                )
            )
            != 0
        ):
            PrintUtils.print_error("配置npm prefix失败")
            return False

        FileUtils.find_replace_sub(
            bashrc,
            "# >>> npm global bin >>>",
            "# <<< npm global bin <<<",
            "",
        )
        FileUtils.append(
            bashrc,
            '# >>> npm global bin >>>\nexport PATH="{}:$PATH"\n# <<< npm global bin <<<'.format(
                npm_global_bin
            ),
        )
        self._run_cmd('export PATH="{}:$PATH"'.format(npm_global_bin), 1)
        PrintUtils.print_success("已配置用户级npm全局目录: {}".format(npm_global_dir))
        return True

    def _install_apt_base(self):
        self._run_cmd(
            "sudo rm -f /etc/apt/sources.list.d/nodesource.sources /etc/apt/sources.list.d/nodesource.list",
            10,
            "移除NodeSource源避免依赖冲突...",
        )
        if not AptUtils.checkapt():
            return False
        result = self._run_cmd(
            "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs npm",
            300,
            "先通过apt安装Node.js基础环境...",
        )
        return self._code(result) == 0

    def _arch_name(self):
        arch_result = self._run_cmd("dpkg --print-architecture", 5)
        if self._code(arch_result) != 0 or len(self._out(arch_result)) == 0:
            return None
        arch = str(self._out(arch_result)[0]).strip()
        if arch == "amd64":
            return "x64"
        if arch == "arm64":
            return "arm64"
        return None

    def _get_latest_tarball_name(self, shasum_url, arch_name):
        try:
            with urllib.request.urlopen(shasum_url, timeout=20) as resp:
                data = resp.read().decode("utf-8", "ignore")
        except Exception:
            return None

        target = "linux-{}.tar.xz".format(arch_name)
        for line in data.splitlines():
            if target in line:
                parts = line.strip().split()
                if len(parts) >= 2:
                    return parts[-1]
        return None

    def _resolve_tar_url(self, target_major, arch_name):
        urls = []

        # 1) TUNA
        tuna_base = "https://mirrors.tuna.tsinghua.edu.cn/nodejs-release"
        try:
            with urllib.request.urlopen(tuna_base + "/index.json", timeout=20) as resp:
                index_data = json.loads(resp.read().decode("utf-8", "ignore"))
            versions = []
            for item in index_data:
                ver = str(item.get("version", ""))
                if ver.startswith("v{}.".format(target_major)):
                    parts = ver[1:].split(".")
                    if (
                        len(parts) >= 3
                        and parts[0].isdigit()
                        and parts[1].isdigit()
                        and parts[2].isdigit()
                    ):
                        versions.append(
                            (int(parts[0]), int(parts[1]), int(parts[2]), ver)
                        )
            if len(versions) > 0:
                versions.sort(reverse=True)
                best_ver = versions[0][3]
                tar_name = "node-{}-linux-{}.tar.xz".format(best_ver, arch_name)
                urls.append(
                    ("{}/{}/{}".format(tuna_base, best_ver, tar_name), tar_name)
                )
        except Exception:
            pass

        # 2) Official Node.js (final fallback)
        official_base = "https://nodejs.org/dist"
        shasum_url = "{}/latest-v{}.x/SHASUMS256.txt".format(
            official_base, target_major
        )
        tar_name = self._get_latest_tarball_name(shasum_url, arch_name)
        if tar_name:
            urls.append(
                (
                    "{}/latest-v{}.x/{}".format(official_base, target_major, tar_name),
                    tar_name,
                )
            )

        return urls

    def _install_from_ustc_tar(self, target_major):
        arch_name = self._arch_name()
        if arch_name is None:
            PrintUtils.print_error("不支持当前架构，无法安装Node.js")
            return False

        tar_urls = self._resolve_tar_url(target_major, arch_name)
        if len(tar_urls) == 0:
            PrintUtils.print_error("未找到Node.js {} 的可用安装包".format(target_major))
            return False

        tar_name = None
        downloaded = False
        for tar_url, cur_tar_name in tar_urls:
            download_result = self._run_cmd(
                "wget --no-proxy {} -O /tmp/nodejs.tar.xz".format(tar_url),
                300,
                "下载Node.js安装包...",
            )
            if self._code(download_result) == 0:
                tar_name = cur_tar_name
                downloaded = True
                break

        if (not downloaded) or tar_name is None:
            return False

        extract_dir = "/opt/nodejs"
        if (
            self._code(
                self._run_cmd(
                    "sudo mkdir -p {} && sudo rm -rf {}/*".format(
                        extract_dir, extract_dir
                    ),
                    20,
                    "解压Node.js安装包...",
                )
            )
            != 0
        ):
            return False

        if (
            self._code(
                self._run_cmd(
                    "sudo tar -xJf /tmp/nodejs.tar.xz -C {}".format(extract_dir), 120
                )
            )
            != 0
        ):
            return False

        node_root = tar_name.replace(".tar.xz", "")
        node_bin = "{}/{}/bin".format(extract_dir, node_root)
        self._run_cmd("sudo ln -sf {}/node /usr/local/bin/node".format(node_bin), 10)
        self._run_cmd("sudo ln -sf {}/npm /usr/local/bin/npm".format(node_bin), 10)
        self._run_cmd("sudo ln -sf {}/npx /usr/local/bin/npx".format(node_bin), 10)
        self._run_cmd("rm -rf /tmp/nodejs.tar.xz", 10)
        return True

    def install_nodejs_version(self, target_major=22, with_registry=True):
        self._cleanup_legacy()
        current_major = self._detect_node_major()
        if current_major is not None and current_major >= target_major:
            PrintUtils.print_success(
                "检测到Node.js版本已满足要求: {}".format(current_major)
            )
            self._fix_node_permissions()
            return self._post_node_setup(target_major, with_registry)

        self._install_apt_base()
        current_major = self._detect_node_major()
        if current_major is not None and current_major >= target_major:
            PrintUtils.print_success(
                "通过apt安装完成，当前Node.js版本: {}".format(current_major)
            )
            self._fix_node_permissions()
            return self._post_node_setup(target_major, with_registry)

        if not self._install_from_ustc_tar(target_major):
            PrintUtils.print_error("Node.js安装失败，请检查网络或镜像可用性")
            return False

        verify_node = self._run_cmd("node -v", 10, "验证Node.js版本...")
        verify_npm = self._run_cmd("npm -v", 10, "验证npm版本...")
        verify_sudo_npm = self._run_cmd("sudo npm -v", 10, "验证sudo环境npm可用性...")
        if (
            self._code(verify_node) != 0
            or self._code(verify_npm) != 0
            or self._code(verify_sudo_npm) != 0
        ):
            PrintUtils.print_error("Node.js或npm验证失败，请重新执行安装")
            return False

        self._fix_node_permissions()
        return self._post_node_setup(target_major, with_registry)

    def install_nodejs(self):
        target_major = self._choose_target_major()
        if target_major is None:
            return False
        return self.install_nodejs_version(target_major)

    def run(self):
        self.install_nodejs()
