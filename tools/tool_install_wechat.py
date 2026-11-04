# -*- coding: utf-8 -*-
import os
import platform
import re
import shutil
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,ChooseTask,DockerUtils
from .base import osversion,osarch
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装微信"
        self.type = BaseTool.TYPE_INSTALL
        self.author = '小鱼'

    def get_wechat_scripts(self,name,build):
        return DockerUtils.permission_check_sh + """xhost +local: >> /dev/null
echo "请输入指令控制{}: 启动(s) 配置:(w) 关闭(c) 重启(r) 删除(d) 重建(b):"
read choose
case $choose in
s) docker start {};;
r) docker restart {};;
c) docker stop {};;
d) docker stop {} && docker rm {};;
w) docker exec --user=wechat {} /bin/sh  -c "WINEPREFIX=/home/wechat/.deepinwine/Deepin-WeChat deepin-wine winecfg";;
b) {};;
esac
newgrp docker
""".format(name,name,name,name,name,name,name,build)

    def install_wechat(self):
        """
        # 原来的 [2] 桌面版本(v2.1.1, 优麒麟打包的 weixin) 10-28 下线: 装上会把 /etc/lsb-release 换成麒麟的
        # (直接读这个文件的程序会把系统认成麒麟), 卸载脚本还会出错; 官方 Linux 版早已可用.
        # 编号 3、4 不变, 免得网上教程和用户的配置文件对不上
        # https://fishros.org.cn/forum/topic/195
        """
        wechat_version_dic = {1:"Docker版本",3:"墙裂推荐:官方Linux版本",4:"一键清理微信"}
        code,_ = ChooseTask(wechat_version_dic,"请选择微信版本(两个版本区别对比:https://fishros.org.cn/forum/topic/195):",False).run()
        if code==3:
            return self.install_official()
        if code == 1:
            run_tool_file('tools.tool_install_docker')
            user =  FileUtils.getusers()[0]
            name = 'wechat'
            inputs = 'fcitx'
            bashrc = '/home/{}/.bashrc'.format(user)
            bin_path = "/home/{}/.fishros/bin/".format(user)
            home = "/home/{}".format(user)
            version_dic = {1:"ibus(系统默认)",2:"fcitx"}
            code,_ = ChooseTask(version_dic,"请选择系统输入法版本(如果不知道怎么选,请选1-ibus):",False).run()
            if code == 1: inputs='ibus'
            file_path = '/home/{}/.WeChatFiles'.format(user,name)
            CmdTask('mkdir -p {}'.format(file_path),os_command=True).run()
            PrintUtils.print_info("正在为您拉取微信镜像")
            CmdTask('sudo docker pull bestwu/wechat ',os_command=True).run()
            CmdTask('sudo docker pull bestwu/wechat ',os_command=True).run()
            PrintUtils.print_info("正在为创建安装微信")
            build = 'sudo docker run -d --name wechat --device /dev/snd --ipc="host"  -v /tmp/.X11-unix:/tmp/.X11-unix  \
            -v {}:/WeChatFiles  -v {}:/home/wechat -e DISPLAY=unix$DISPLAY  -e XMODIFIERS=@im={}  -e QT_IM_MODULE={}  -e GTK_IM_MODULE={}  -e AUDIO_GID=`getent group audio | cut -d: -f3` bestwu/wechat'.format(file_path,home,inputs,inputs,inputs)
            result = CmdTask(build,os_command=False).run()

            if result[0] != 0: PrintUtils.print_error("失败了。。请到社区或群聊反馈:{}".format(result[1]+result[2]))
            PrintUtils.print_info("===========================================")
            PrintUtils.print_success("已为你安装完成wechat，稍后会弹窗登录")
            # 创建微信脚本
            FileUtils.new(bin_path,name,self.get_wechat_scripts(name,build))
            FileUtils.find_replace_sub(bashrc,"# >>> fishros scripts >>>","# <<< fishros scripts <<<", "")
            FileUtils.append(bashrc,'# >>> fishros scripts >>>\nexport PATH=$PATH:{} \n# <<< fishros scripts <<<'.format(bin_path))
            CmdTask('sudo chmod 777 {}'.format(bin_path+name),os_command=True).run()

            PrintUtils.print_info("=================后续使用指令==================")
            PrintUtils.print_warn("后续可在任意终端输入{}来启动/停止微信".format(name))
            PrintUtils.print_info("=================文件存储位置==================")
            PrintUtils.print_warn("微信所有文件放到你的主目录下：WeChatFiles")
            PrintUtils.print_info("=================分辨率/目录等配置==============")
            PrintUtils.print_warn("在任意终端输入wechat，选w-回车进入配置页面")
        if code==4:
            # 清理完回到微信菜单: 常常是清理后接着装官方版, 不装了选 0 回主菜单
            self.clean_wechat()
            return self.install_wechat()

    # 一键清理时认得的微信包, 其它名字以 wechat 开头的包按包名显示
    wechat_pkg_names = {
        "wechat": "官方 Linux 版微信",
        "wechat-beta": "旧版微信 wechat-beta",
        "wechat-linux-spark": "星火商店版微信",
    }

    def clean_wechat(self):
        """
        一键清理微信: 先查有哪些, 只清理真正装了的(原来不管有没有都跑一遍 apt/docker, 满屏报错也不说清了什么),
        最后列出清理了什么. 主目录里的聊天记录和文件不删
        """
        cleaned = []
        if self.remove_desktop():
            cleaned.append("已下线的桌面版微信 v2.1.1(weixin)")

        result = CmdTask("dpkg-query -W -f='${Package}\\t${Status}\\n' 'wechat*'").run()
        pkgs = [line.split("\t")[0] for line in result[1]
                if "\t" in line and ("installed" in line or "config-files" in line) and "not-installed" not in line]
        if pkgs:
            CmdTask("sudo apt purge -y {}".format(" ".join(pkgs)),os_command=True).run()
            cleaned += [self.wechat_pkg_names.get(p, p) for p in pkgs if not self.installed(p)]

        if shutil.which("docker"):
            if "wechat" in "".join(CmdTask("sudo docker ps -a --filter name=^wechat$ --format '{{.Names}}'").run()[1]):
                CmdTask("sudo docker rm -f wechat",os_command=True).run()
                cleaned.append("Docker 版微信容器(wechat)")
            if CmdTask("sudo docker image inspect bestwu/wechat").run()[0] == 0:
                CmdTask("sudo docker image rm bestwu/wechat",os_command=True).run()
                cleaned.append("Docker 版微信镜像(bestwu/wechat)")

        PrintUtils.print_info("=" * 50)
        if not cleaned:
            PrintUtils.print_success("没有发现已安装的微信, 不需要清理")
            return True
        PrintUtils.print_success("微信清理完成, 共清理了:")
        for item in cleaned:
            PrintUtils.print_success("  - " + item)
        PrintUtils.print_info("聊天记录和收发的文件保存在你的主目录里, 这次没有删除; 确定不要了可以自己手动删掉")
        return True

    # 腾讯官方 Linux 微信各架构的安装包, 键是 uname -m 的结果
    # (不用 dpkg --print-architecture: base.getArch 会把 32 位 armhf 也报成 arm64)
    official_debs = {
        "x86_64": "WeChatLinux_x86_64.deb",
        "aarch64": "WeChatLinux_arm64.deb",
        "loongarch64": "WeChatLinux_LoongArch.deb",
    }

    @staticmethod
    def installed(pkg):
        status = CmdTask("dpkg-query -W -f='${{Status}}' {}".format(pkg)).run()
        return "install ok installed" in "".join(status[1])

    def remove_desktop(self):
        """
        清理已下线的桌面版 2.1.1(weixin). 它装上时把原来的 /etc/lsb-release 改名成 lsb-release-test、换上麒麟的,
        卸载脚本再挪回去; 原文件不在时卸载脚本报错, 包卡在卸了一半的状态. 所以先保证有 lsb-release-test 再卸,
        卸完要是还是麒麟的(原文件早就丢了), 按 /etc/os-release 重新生成
        """
        if CmdTask("dpkg-query -W weixin").run()[0] != 0:
            return False
        PrintUtils.print_info("检测到已下线的桌面版微信 v2.1.1, 一并清理并恢复被它改成麒麟的系统版本信息")
        # 直接 purge 会把卸载脚本跑两遍(remove、purge 各一次), 第二遍时 lsb-release-test 已被挪走而报错,
        # 所以分两步, 每步之前都补上 lsb-release-test
        for action in ("remove", "purge"):
            if not os.path.exists("/etc/lsb-release-test"):
                CmdTask("sudo cp /etc/lsb-release /etc/lsb-release-test").run()
            CmdTask("sudo apt {} -y weixin".format(action),os_command=True).run()
        with open("/etc/lsb-release") as f:
            if "Kylin" not in f.read():
                return True
        info = {}
        with open("/etc/os-release") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    info[key] = value.strip('"')
        with open("/tmp/fishros_lsb_release", "w") as f:
            f.write('DISTRIB_ID={}\nDISTRIB_RELEASE={}\nDISTRIB_CODENAME={}\nDISTRIB_DESCRIPTION="{}"\n'.format(
                info.get("NAME", "Ubuntu").split()[0], info.get("VERSION_ID", ""),
                info.get("VERSION_CODENAME", ""), info.get("PRETTY_NAME", "")))
        CmdTask("sudo cp /tmp/fishros_lsb_release /etc/lsb-release").run()
        PrintUtils.print_success("已恢复 /etc/lsb-release: {}".format(info.get("PRETTY_NAME", "")))
        return True

    def install_official(self):
        """
        官方 Linux 版微信. 社区帖 4843: 装过旧版 wechat-beta 时, 新包要覆盖它的 wechat.desktop, dpkg 报错没装上,
        原来不看结果照样提示安装完成. 现在 dpkg 报文件冲突时说明是哪个旧包、问要不要卸载后重装, 最后确认装上了才提示成功
        """
        machine = platform.machine()
        deb = self.official_debs.get(machine)
        if not deb:
            PrintUtils.print_error("官方 Linux 版微信只提供 x86_64、arm64、龙芯(LoongArch) 安装包, 当前系统架构 {} 不支持".format(machine))
            return False
        CmdTask('wget -T 15 -t 3 https://dldir1v6.qq.com/weixin/Universal/Linux/{} -O /tmp/wechat.deb'.format(deb),os_command=True).run()
        if CmdTask('dpkg-deb -I /tmp/wechat.deb').run()[0] != 0:
            PrintUtils.print_error("微信安装包下载不完整, 请检查网络后重试")
            return False

        result = CmdTask('sudo dpkg -i /tmp/wechat.deb').run()
        if result[0] != 0:
            # 中文: 它同时被包含于软件包 wechat-beta 1.0.0.145; 英文: which is also in package wechat-beta 1.0.0.145
            owners = re.findall(r"(?:包含于软件包|also in package)\s+(\S+)", "\n".join(result[1] + result[2]))
            old = [p for p in dict.fromkeys(owners) if p != "wechat"]
            if old:
                PrintUtils.print_warn("系统里已有旧版微信 {}, 和官方新版的文件冲突, 需要先卸载旧版才能安装".format(" ".join(old)))
                code,_ = ChooseTask({1:"卸载旧版 {} 后继续安装".format(" ".join(old))},"是否卸载旧版:",False).run()
                if code != 1:
                    return BaseTool.BACK
                CmdTask('sudo apt remove -y {}'.format(" ".join(old)),os_command=True).run()
                CmdTask('sudo dpkg -i /tmp/wechat.deb',os_command=True).run()
        # 缺依赖时 dpkg 会留下未配置完的包, 让 apt 补装依赖并配置好
        CmdTask('sudo apt --fix-broken install -y',os_command=True).run()

        if self.installed("wechat"):
            PrintUtils.print_success("已为你安装完成官方 Linux 版微信~ 可在应用列表里找到「微信」")
            return True
        PrintUtils.print_error("官方 Linux 版微信没有装上, 请把上面的报错发到鱼香社区反馈: https://fishros.org.cn/forum")
        return False

    def run(self):
        return self.install_wechat()

# sudo docker run -d --name wechat1 --device /dev/snd --ipc="host"  -v /tmp/.X11-unix:/tmp/.X11-unix  -v $HOME/WeChatFiles:/WeChatFiles  -e DISPLAY=unix$DISPLAY  -e XMODIFIERS=@im=fcitx  -e QT_IM_MODULE=fcitx  -e GTK_IM_MODULE=fcitx  -e AUDIO_GID=`getent group audio | cut -d: -f3`  bestwu/wechat