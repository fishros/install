# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file
from .base import os

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_CONFIG
        self.name = "python change source"
        self.autor = 'songHat'

    def run(self):
        #正式的运行
        PrintUtils.print_delay('runing python_source')
        port = "https://pypi.mirrors.ustc.edu.cn/simple/"
        
        path = '~/.pip/pip.conf'
        # delete 
        if FileUtils.exists(path):
            FileUtils.delete(path)

        data = "[global]\nindex-url = {}".format(port)
        CmdTask(f"sudo touch {path}").run()
        CmdTask(f"sudo chmod 777 {path}").run()
        CmdTask(f'sudo echo "{data}" > {path}').run()
        CmdTask(f'pip config list').run()
        PrintUtils.print_delay('配置成功（如果使用国内源下载包，记得关闭代理）')


