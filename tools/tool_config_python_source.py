# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, AptUtils, ChooseTask
from .base import osversion
from .base import run_tool_file
from .base import os

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_CONFIG
        self.name = "python change source"
        self.author = 'songHat'

    def run(self):
        # 正式的运行
        port = "https://pypi.mirrors.ustc.edu.cn/simple/"
        
        homes = FileUtils.getusershome()
        for home in homes:
            pip_dir = os.path.join(home, '.pip')
            pip_conf = os.path.join(pip_dir, 'pip.conf')

            # Delete .pip directory if it exists
            if FileUtils.exists(pip_dir):
                FileUtils.delete(pip_dir)

            # Create the .pip directory
            os.mkdir(pip_dir)

            # Write the configuration to pip.conf
            data = "[global]\nindex-url = {}".format(port)
            with open(pip_conf, 'w') as f:
                f.write(data)

            # Set the appropriate permissions
            CmdTask(f"sudo chmod 777 {pip_conf}").run()

            # Verify pip configuration
            CmdTask('pip config list').run()

        PrintUtils.print_delay('配置成功（如果使用国内源下载包，记得关闭代理）')
