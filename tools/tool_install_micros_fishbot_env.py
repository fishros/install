# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.name = "安装PlateformIO MicroROS开发环境(支持Fishbot)"
        self.type = BaseTool.TYPE_INSTALL
        self.autor = '小鱼'

    def install_nodejs(self):
        PrintUtils.print_warn("注意:目前本工具仅在Ubuntu22.04上测试通过")

        PrintUtils.print_info("开始下载小鱼配置好的PlateformIO核心包及开发库~")

        target_path = "/tmp/platformio"
        FileUtils.delete(target_path)
        CmdTask(f'rm -rf {target_path} && mkdir {target_path}',os_command=True).run()

        for i in range(0,3):
            repo = f"platformio0{i}"
            tar = f"platformio.0{i}"
            PrintUtils.print_info(f"正在下载第{i}部分数据~")
            CmdTask(f'git clone https://gitee.com/ohhuo/{repo}',os_command=True,path=target_path).run()
            PrintUtils.print_info(f"下载完成第{i}部分数据,开始进行组装~")
            CmdTask(f'cat {repo}/{repo}.* > {target_path}/{tar}',os_command=True,path=target_path).run()
            PrintUtils.print_info("组装完成~")
        CmdTask('cat platformio.* > platformio.tar.gz',os_command=True,path=target_path).run()
        PrintUtils.print_info("下载完成,接下来为你解压安装PlateformIO~")
        
        user = FileUtils.getusers()[0]
        if user!='root':
            CmdTask(f'tar -xzvf platformio.tar.gz -C /home/{user}/',os_command=True,path=target_path).run()
        else:
            CmdTask(f'tar -xzvf platformio.tar.gz -C /root/',os_command=True,path=target_path).run()
        PrintUtils.print_info("解压完成,接下来你可以到vscode里下载platformio插件并新建工程了~!")


    def run(self):
        self.install_nodejs()

