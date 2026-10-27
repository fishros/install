# -*- coding: utf-8 -*-
import os
import time
import urllib.error
import urllib.request
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file



ubuntu_ports_sources_template = """
deb <sources>/ <code-name> main restricted universe multiverse
deb <sources>/ <code-name>-updates main restricted universe multiverse
deb <sources>/ <code-name>-backports main restricted universe multiverse
deb <sources>/ <code-name>-security main restricted universe multiverse
"""
ubuntu_amd64_sources_template = """
deb <sources>/ <code-name> main restricted universe multiverse
deb <sources>/ <code-name>-updates main restricted universe multiverse
deb <sources>/ <code-name>-backports main restricted universe multiverse
deb <sources>/ <code-name>-security main restricted universe multiverse
"""
# Debian 10 及更早: 安全源路径是 <code-name>/updates
debian_old_sources_template = """
deb <sources>/ <code-name> main contrib non-free
deb <sources>/ <code-name>-updates main contrib non-free
deb <sources>/ <code-name>-backports main contrib non-free
deb <sources>-security <code-name>/updates main contrib non-free
"""
# Debian 11 起: 安全源改为 <code-name>-security
debian_amd64_sources_template = """
deb <sources>/ <code-name> main contrib non-free
deb <sources>/ <code-name>-updates main contrib non-free
deb <sources>/ <code-name>-backports main contrib non-free
deb <sources>-security/ <code-name>-security main contrib non-free
"""
# Debian 12 起: 固件单独拆到 non-free-firmware
debian_firmware_sources_template = """
deb <sources>/ <code-name> main contrib non-free non-free-firmware
deb <sources>/ <code-name>-updates main contrib non-free non-free-firmware
deb <sources>/ <code-name>-backports main contrib non-free non-free-firmware
deb <sources>-security/ <code-name>-security main contrib non-free non-free-firmware
"""
ubuntu_ports_deb822_template = """
Types: deb
URIs: <sources>/
Suites: <code-name> <code-name>-updates <code-name>-backports
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

Types: deb
URIs: <sources>/
Suites: <code-name>-security
Components: main universe restricted multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
"""
ubuntu_amd64_deb822_template = """
Types: deb
URIs: <sources>/
Suites: <code-name> <code-name>-updates <code-name>-backports
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

# 以下安全更新软件源包含了官方源与镜像站配置，如有需要可自行修改注释切换
Types: deb
URIs: <sources>/
Suites: <code-name>-security
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
"""

# Ubuntu 24.04 起默认使用 deb822 格式的 ubuntu.sources, 不再用 sources.list
ubuntu_deb822_file = '/etc/apt/sources.list.d/ubuntu.sources'

# 系统镜像只用 http: 老系统证书过期、设备时钟不准时 https 会失败(与一键安装其它下载一致).
# 2026-10 实测: kernel.org 在国内只有一百多 KB/s, 网易 163 连不上, 阿里云 Ubuntu 带宽很低, 都不放进来
ubuntu_mirrors = [
    ("清华大学", "http://mirrors.tuna.tsinghua.edu.cn/ubuntu"),
    ("中国科学技术大学", "http://mirrors.ustc.edu.cn/ubuntu"),
    ("中山大学", "http://mirror.sysu.edu.cn/ubuntu"),
    ("北京外国语大学", "http://mirrors.bfsu.edu.cn/ubuntu"),
    ("南京大学", "http://mirror.nju.edu.cn/ubuntu"),
    ("华为云", "http://repo.huaweicloud.com/ubuntu"),
    ("Ubuntu官方", "http://archive.ubuntu.com/ubuntu"),
]
# arm64/armhf(树莓派、Jetson 等)用 ubuntu-ports
ubuntu_ports_mirrors = [
    ("清华大学", "http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports"),
    ("中国科学技术大学", "http://mirrors.ustc.edu.cn/ubuntu-ports"),
    ("中山大学", "http://mirror.sysu.edu.cn/ubuntu-ports"),
    ("南京大学", "http://mirror.nju.edu.cn/ubuntu-ports"),
    ("华为云", "http://repo.huaweicloud.com/ubuntu-ports"),
    ("Ubuntu官方", "http://ports.ubuntu.com/ubuntu-ports"),
]
# 已停止支持的 Ubuntu 版本(如 24.10)会从普通镜像删除, 只能用旧版本归档源, 所有架构都在里面
ubuntu_old_mirrors = [
    ("中国科学技术大学(旧版本归档)", "http://mirrors.ustc.edu.cn/ubuntu-old-releases/ubuntu"),
    ("南京大学(旧版本归档)", "http://mirror.nju.edu.cn/ubuntu-old-releases/ubuntu"),
    ("Ubuntu官方(旧版本归档)", "http://old-releases.ubuntu.com/ubuntu"),
]
# Debian 的镜像不区分架构, arm64/armhf 和 amd64 用同一套地址
debian_mirrors = [
    ("清华大学", "http://mirrors.tuna.tsinghua.edu.cn/debian"),
    ("中国科学技术大学", "http://mirrors.ustc.edu.cn/debian"),
    ("中山大学", "http://mirror.sysu.edu.cn/debian"),
    ("阿里云", "http://mirrors.aliyun.com/debian"),
    ("南京大学", "http://mirror.nju.edu.cn/debian"),
    ("华为云", "http://repo.huaweicloud.com/debian"),
    ("Debian官方", "http://deb.debian.org/debian"),
]


class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_CONFIG
        self.name = "一键更换系统源"
        self.author = '小鱼'
        self.use_deb822 = False
        self.cancelled = False
        self.backups = []
        self.ranking = {}
        self.source_names = {}


    def add_ros_source(self):
        """快速添加ROS源"""
        dic = {1:"添加ROS/ROS2源",2:"不添加ROS/ROS2源"}
        code,result = ChooseTask(dic, "请问是否添加ROS和ROS2源？").run()
        if code!=1: return
        tool = run_tool_file('tools.tool_install_ros',authorun=False)
        if not tool.support_install(): return False
        tool.add_key()
        tool.add_source()

    def backup_path(self, path):
        """把要清理的源文件/目录改名备份, 而不是直接删除, 出问题可以手动恢复"""
        if not os.path.exists(path):
            return None
        backup = '{}.fishros-bak-{}'.format(path, time.strftime('%Y%m%d%H%M%S'))
        CmdTask('sudo mv {} {}'.format(path, backup)).run()
        self.backups.append((backup, path))
        return backup

    def backup_third_party_sources(self):
        """
        把 sources.list.d 里的第三方源(除系统自己的 ubuntu.sources 外)挪到备份目录.
        返回备份目录, 没有第三方源时返回 None
        """
        src_dir = '/etc/apt/sources.list.d'
        if not os.path.isdir(src_dir):
            return None
        files = [f for f in os.listdir(src_dir) if f != 'ubuntu.sources']
        if not files:
            return None
        backup = '{}.fishros-bak-{}'.format(src_dir, time.strftime('%Y%m%d%H%M%S'))
        CmdTask('sudo mkdir -p {}'.format(backup)).run()
        for f in files:
            CmdTask('sudo mv {}/{} {}/'.format(src_dir, f, backup)).run()
        self.backups.append((backup, src_dir))
        return backup

    def restore_sources(self):
        """用户中途选了退出: 把这次挪走、改掉的源文件恢复回去, 系统源保持换源前的样子"""
        for backup, original in reversed(self.backups):
            if original == '/etc/apt/sources.list.d':
                CmdTask('sudo sh -c "mv {0}/* {1}/ && rmdir {0}"'.format(backup, original)).run()
            else:
                CmdTask('sudo mv {} {}'.format(backup, original)).run()
        self.backups = []
        if getattr(self, 'original_deb822', None) is not None:
            FileUtils.new('/etc/apt/sources.list.d/', 'ubuntu.sources', self.original_deb822)
        PrintUtils.print_warn('已取消换源, 系统源已恢复成原来的配置')

    def clean_old_source(self, auto=False):
        """备份旧的源配置. 用户在提问里选了退出时返回 False, 这时还没有动任何文件"""
        if auto:
            # 全自动模式: 只换系统源, 第三方源先保留, apt update 失败时再挪走(见 change_sys_source)
            code = 1
            self.source_method_code = 1
        else:
            dic = {1:"仅更换系统源",2:"更换系统源并清理第三方源"}
            code,result = ChooseTask(dic, "请选择换源方式,如果不知道选什么请选2").run()
            if code == 0:
                return False
            PrintUtils.print_info("源选择方式说明:")
            PrintUtils.print_info("1. 自动测速选择最快的源: 系统将自动测试各个源的速度，并选择最快的源")
            PrintUtils.print_info("2. 根据测速结果手动选择源: 系统将测试各个源的速度，然后让您从测试结果中选择")
            dic_source_method = {1:"自动测速选择最快的源", 2:"根据测速结果手动选择源"}
            self.source_method_code, _ = ChooseTask(dic_source_method, "请选择源的选择方式").run()
            if self.source_method_code == 0:
                return False

        # 清理前先记下系统是否使用 deb822 格式(24.04+), 否则清理三方源时会连 ubuntu.sources 一起挪走, 就判断不出来了
        self.use_deb822 = os.path.exists(ubuntu_deb822_file)
        self.original_deb822 = None
        if self.use_deb822:
            with open(ubuntu_deb822_file, encoding='utf-8') as f:
                self.original_deb822 = f.read()
            backup = '/etc/apt/ubuntu.sources.fishros.bak'
            if not os.path.exists(backup):
                CmdTask('sudo cp {} {}'.format(ubuntu_deb822_file, backup)).run()
        self.backup_path('/etc/apt/sources.list')
        if code==2:
            backup_dir = self.backup_third_party_sources()
            if backup_dir:
                PrintUtils.print_info('第三方源已备份到 {}, 如需恢复可把里面的文件挪回 /etc/apt/sources.list.d/'.format(backup_dir))
            # fix add source failed before config system source
            CmdTask('sudo mkdir -p /etc/apt/sources.list.d').run()
        return True

    def get_debian_template(self, codename):
        if codename in ('wheezy', 'jessie', 'stretch', 'buster'):
            return debian_old_sources_template
        if codename == 'bullseye':
            return debian_amd64_sources_template
        return debian_firmware_sources_template

    @staticmethod
    def measure_source(url, codename, timeout=4):
        """
        下载镜像里的 dists/<代号>/Release 测速: 测的是真实下载速度(原来只测首包延迟, 带宽很低的镜像也会排第一),
        同时确认镜像里确实有这个系统版本. 返回 (KB/s, 状态), 状态: ok / missing(镜像里没有) / fail(连不上)
        """
        # 带上 apt 的 User-Agent: 镜像对 apt 和其它下载工具的策略可能不同(中科大会拒绝 wget)
        request = urllib.request.Request(
            '{}/dists/{}/Release'.format(url, codename), headers={'User-Agent': 'Debian APT-HTTP/1.3'})
        start = time.time()
        size = 0
        try:
            with urllib.request.urlopen(request, timeout=timeout) as resp:
                while time.time() - start < timeout:
                    chunk = resp.read(16384)
                    if not chunk:
                        break
                    size += len(chunk)
        except urllib.error.HTTPError as e:
            return 0, 'missing' if e.code == 404 else 'fail'
        except Exception:
            return 0, 'fail'
        if size == 0:
            return 0, 'fail'
        return size / 1024.0 / max(time.time() - start, 0.001), 'ok'

    def rank_mirrors(self, mirrors, codename):
        """逐个测速, 返回按速度从快到慢排好的地址列表, 以及是否每个连得上的镜像都没有这个系统版本"""
        speeds = {}
        missing = 0
        for name, url in mirrors:
            self.source_names[url] = name
            speed, status = self.measure_source(url, codename)
            # 镜像偶尔会有一次连接超时(实测每轮都有一两个), 再试一次, 免得把最快的镜像误判掉
            if status == 'fail':
                speed, status = self.measure_source(url, codename)
            if status == 'ok':
                speeds[url] = speed
                PrintUtils.print_success('- {}\t{}\t速度: {:.0f}KB/s'.format(name, url, speed))
            elif status == 'missing':
                missing += 1
                PrintUtils.print_info('- {}\t{}\t没有 {} 版本'.format(name, url, codename))
            else:
                PrintUtils.print_info('- {}\t{}\t连接失败'.format(name, url))
        ranked = sorted(speeds, key=speeds.get, reverse=True)
        return ranked, missing > 0 and not ranked

    def get_source_by_system(self,system,codename,arch,failed_sources=[], return_all=False):
        if system == 'ubuntu':
            mirrors = ubuntu_mirrors if arch == 'amd64' else ubuntu_ports_mirrors
            if arch == 'amd64':
                template = ubuntu_amd64_deb822_template if self.use_deb822 else ubuntu_amd64_sources_template
            else:
                template = ubuntu_ports_deb822_template if self.use_deb822 else ubuntu_ports_sources_template
        else:
            mirrors = debian_mirrors
            template = self.get_debian_template(codename)

        # 只测一次速, 换下一个源时直接用排好的顺序, 不再重新测
        key = (system, codename, arch)
        if key not in self.ranking:
            PrintUtils.print_delay('正在测试各个镜像源的下载速度, 为您挑选最快的:', 0.002)
            ranked, eol = self.rank_mirrors(mirrors, codename)
            if eol and system == 'ubuntu':
                PrintUtils.print_warn('{} 已停止官方支持, 普通镜像里已经没有它了, 改用旧版本归档源'.format(codename))
                ranked, _ = self.rank_mirrors(ubuntu_old_mirrors, codename)
            self.ranking[key] = ranked

        sources = [source for source in self.ranking[key] if source not in failed_sources]
        if not sources:
            return None, None
        if return_all:
            return sources, template
        return sources[0], template

    def replace_source(self,failed_sources=[]):
        arch = AptUtils.getArch()
        name = osversion.get_name()
        codename = osversion.get_codename()
        if name.find("ubuntu")>=0:
            system = 'ubuntu'
        elif name.find("debian")>=0:
            system = 'debian'
        else:
            PrintUtils.print_error('当前系统{}暂不支持一键换源'.format(name))
            return None
        if not codename:
            PrintUtils.print_error('获取系统代号失败, 无法自动换源, 请检查 /etc/os-release')
            return None

        PrintUtils.print_delay('检测到当前系统:{} 架构:{} 代号:{},正在为你搜索适合的源...'.format(system,arch,codename))

        # 根据用户选择的方式获取源
        if getattr(self, 'source_method_code', 1) == 2:
            # 根据测速结果手动选择源
            sorted_sources, template = self.get_source_by_system(system, codename, arch, failed_sources, return_all=True)
            if not sorted_sources:
                return None
            source_dict = {}
            for i, src in enumerate(sorted_sources, 1):
                source_dict[i] = '{} {}'.format(self.source_names.get(src, ''), src)
            PrintUtils.print_info("请从测速结果中选择您想使用的镜像源(已按速度从快到慢排列):")
            code, _ = ChooseTask(source_dict, "请选择一个镜像源").run()
            if code == 0:
                self.cancelled = True
                return None
            source = sorted_sources[code - 1]
            PrintUtils.print_success('您选择的镜像源:{}'.format(source_dict[code]))
        else:
            # 自动测速选择源
            source, template = self.get_source_by_system(system, codename, arch, failed_sources)
            if not source: return None
            PrintUtils.print_success('为您选择最快镜像源:{} {}'.format(self.source_names.get(source, ''), source))

        data = template.replace("<code-name>",codename).replace('<sources>',source.rstrip('/'))
        if self.use_deb822:
            FileUtils.new('/etc/apt/sources.list.d/','ubuntu.sources',data)
        else:
            FileUtils.new('/etc/apt/','sources.list',data)
        return source


    def change_sys_source(self, auto=False):
        self.cancelled = False
        self.current_source = None
        self.failed_sources = []
        if not self.clean_old_source(auto=auto):
            self.cancelled = True
            PrintUtils.print_warn('已取消换源, 系统源没有改动')
            return

        failed_sources = []
        result = (-1, [], [])
        source = self.replace_source(failed_sources)
        if source:
            PrintUtils.print_delay("替换镜像源完成，尝试进行更新....")
            result = CmdTask('sudo apt update',100).run()
            # 全自动模式下保留了第三方源, 更新失败多半是它们的问题(密钥过期/源失效), 先挪走再试
            if result[0] != 0 and auto:
                backup_dir = self.backup_third_party_sources()
                if backup_dir:
                    PrintUtils.print_warn('更新失败, 已把可能有问题的第三方源备份到 {} 后重试'.format(backup_dir))
                    result = CmdTask('sudo apt update',100).run()
            if result[0] != 0:
                if getattr(self, 'source_method_code', 1) == 2:
                    PrintUtils.print_warn("您选择的源更新失败，请重新选择其他源")
                while result[0] != 0:
                    failed_sources.append(source)
                    PrintUtils.print_warn("更新失败，尝试更换其他源")
                    source = self.replace_source(failed_sources)
                    if not source:
                        break
                    result = CmdTask('sudo apt update',100).run()

        if self.cancelled:
            self.restore_sources()
            return
        if not source:
            PrintUtils.print_error("没有找到合适的镜像源,臣妾告退!")
            return

        self.current_source = source if result[0] == 0 else None
        self.failed_sources = failed_sources
        if result[0]==0:
            PrintUtils.print_success("搞定了,不信你看,累死宝宝了，还不快去给小鱼点个赞~")
            PrintUtils.print_info(result[1])
        PrintUtils.print_success("镜像更新完成.....")

    def switch_to_next_source(self):
        """
        全自动模式: 当前系统镜像在安装中途下载失败(限流/断连)时, 换下一个最快的镜像并更新索引.
        返回新镜像地址, 没有可用镜像时返回 None
        """
        if not getattr(self, 'current_source', None):
            return None
        self.exclude_server(self.current_source)
        source = self.replace_source(self.failed_sources)
        while source:
            if CmdTask('sudo apt update', 100).run()[0] == 0:
                self.current_source = source
                return source
            self.exclude_server(source)
            source = self.replace_source(self.failed_sources)
        return None

    def exclude_server(self, source):
        """同一台服务器的 http/https 地址一起排除, 否则"换镜像"可能只是换了个协议"""
        address = source.split('://', 1)[-1]
        self.failed_sources.extend(['http://' + address, 'https://' + address])

    def run(self):
        # 正式的运行
        self.change_sys_source()
        if self.cancelled:
            return
        # 添加 ROS Source
        self.add_ros_source()
