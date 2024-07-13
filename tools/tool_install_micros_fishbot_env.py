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
        user_homes = FileUtils.getusershome()
        user = FileUtils.getusers()[0]
        user_home = user_homes[0]
        # if len(user_homes)>1:
        #     dic = {}
        #     for i in range(len(user_homes)):
        #         dic[i+1] = user_homes[i]
        #     code,result = ChooseTask(dic,"请选择用户目录",array=True).run()    

        PrintUtils.print_info("开始生成安装脚本~")
        install_sh = """export HOME={} && $HOME/.platformio/penv/bin/pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple platformio
echo "开始下载ESP32开发依赖库~"
rm -rf /tmp/pio
mkdir -p /tmp/pio/
cd /tmp/pio
touch platformio.ini
mkdir src
wget http://github.fishros.org/https://raw.githubusercontent.com/fishros/example_micoros_board/main/example01_helloworld/src/main.cpp -O src/main.cpp
echo "[env:featheresp32]" >> platformio.ini
echo "platform = espressif32" >> platformio.ini
echo "board = featheresp32" >> platformio.ini
echo "framework = arduino" >> platformio.ini
source $HOME/.platformio/penv/bin/activate
export http_proxy=http://fishros.org:8899 && export https_proxy=http://fishros.org:8899
pio run
export http_proxy= && export https_proxy=
pio run
rm -rf /tmp/pio
""".format(user_home)
        FileUtils.new('/tmp/', 'install_pio.sh',install_sh)
        CmdTask('sudo -u {} bash /tmp/install_pio.sh'.format(user), os_command=True).run()
        PrintUtils.print_info("安装完成,接下来你可以到vscode里新建工程了~!")

    def run(self):
        self.install_nodejs()

