# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion, osarch
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_INSTALL
        self.name = "一键安装Clash"
        self.autor = '五柳小生'

    def install_sogou(self):
        PrintUtils.print_info("开始根据系统架构，为你下载对应版本的搜狗输入法~")
        if osarch == 'arm64':
            CmdTask('sudo wget https://ime-sec.gtimg.com/202309222309/27ad8a1c31e30bda11c4d713999123a1/pc/dl/gzindex/1680521473/sogoupinyin_4.2.1.145_arm64.deb -O /tmp/sogou.deb',os_command=True).run()
        elif osarch == 'amd64':
            CmdTask('sudo wegt https://ime-sec.gtimg.com/202309221754/8529e970e466dd8f44b1c77a76d419d4/pc/dl/gzindex/1680521603/sogoupinyin_4.2.1.145_amd64.deb, -O /tmp/sogou.deb',os_command=True).run()
        else:
            return False
        PrintUtils.print_info("下载完成，接下来为您安装搜狗输入法")
        # 更新源
        CmdTask("sudo apt update").run()
        # 安装fcitx输入法框架
        CmdTask("sudo apt install fcitx").run()
        # 设置中文语言
        CmdTask("sudo apt install language-pack-zh-hans").run()
        CmdTask("localectl set-locale LANG=zh_CN.utf8").run()
        # 设置fcitx开机自启动
        CmdTask("sudo cp /usr/share/applications/fcitx.desktop /etc/xdg/autostart/").run()
        CmdTask("sudo apt purge ibus").run()
        CmdTask("sudo dpkg -i /tmp/sogou.deb").run()
        # 安装输入法依赖
        CmdTask("sudo apt install libqt5qml5 libqt5quick5 libqt5quickwidgets5 qml-module-qtquick2").run()
        CmdTask("sudo apt install libgsettings-qt1").run()
        CmdTask("rm -rf /tmp/sogou.deb").run()
        PrintUtils.print_info("安装完成~").run()
        PrintUtils.print_info("重启后配置生效,可以在右上角小键盘上查看和选择,是否选择现在重启(y/n):")
        choice = input()
        if choice == 'y':
            CmdTask("reboot")
        else:
            CmdTask("欢迎下次使用")



    def run(self):
        #正式的运行
        self.install_sogou()
