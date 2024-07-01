# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, AptUtils, ChooseTask
from .base import osversion, osarch
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.name = "安装PlateformIO MicroROS开发环境(支持Fishbot)"
        self.type = BaseTool.TYPE_INSTALL
        self.autor = '小鱼'

    def install_nodejs(self):
        CmdTask('sudo apt update && sudo apt install git python3-venv -y', os_command=True).run()
        PrintUtils.print_warn("注意:运行本指令前需要在VS Code 中安装 PlatformIO 插件后再运行本命令")
        user_home = FileUtils.getusershome()[0]
        PrintUtils.print_info("开始安装Platform IO~")
        print(CmdTask('export HOME={} && $HOME/.platformio/penv/bin/pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple platformio'.format(user_home),os_command=True).run())
        PrintUtils.print_info("开始下载ESP32开发依赖库~")
        PrintUtils.print_warn("下载不使用代理会很慢（大约4小时左右），建议运行一键安装14开启代理后，导出终端代理可10分钟装好")
        PrintUtils.print_info("当前进度: 1/7 ")
        CmdTask('export HOME={} && $HOME/.platformio/penv/bin/pio pkg install --global --platform "platformio/espressif32@^6.4.0"'.format(user_home),os_command=True).run()
        PrintUtils.print_info("当前进度: 2/7 ")
        CmdTask('export HOME={} && $HOME/.platformio/penv/bin/pio pkg install --global --tool "platformio/contrib-piohome"'.format(user_home), os_command=True).run()
        PrintUtils.print_info("当前进度: 3/7 ")
        CmdTask('export HOME={} && $HOME/.platformio/penv/bin/pio pkg install --global --tool "platformio/framework-arduinoespressif32"'.format(user_home), os_command=True).run()
        PrintUtils.print_info("当前进度: 4/7 ")
        CmdTask('export HOME={} && $HOME/.platformio/penv/bin/pio pkg install --global --tool "platformio/tool-scons"'.format(user_home), os_command=True).run()
        PrintUtils.print_info("当前进度: 5/7 ")
        CmdTask('export HOME={} && $HOME/.platformio/penv/bin/pio pkg install --global --tool "platformio/tool-mkfatfs"'.format(user_home), os_command=True).run()
        PrintUtils.print_info("当前进度: 6/7 ")
        CmdTask('export HOME={} && $HOME/.platformio/penv/bin/pio pkg install --global --tool "platformio/tool-mkspiffs"'.format(user_home), os_command=True).run()
        PrintUtils.print_info("当前进度: 7/7 ")
        CmdTask('export HOME={} && $HOME/.platformio/penv/bin/pio pkg install --global --tool "platformio/tool-mklittlefs"'.format(user_home), os_command=True).run()

        PrintUtils.print_info("安装,接下来你可以到vscode里新建工程了~!")

    def run(self):
        self.install_nodejs()

