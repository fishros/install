# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.name = "快速备份还原系统工具"
        self.type = BaseTool.TYPE_INSTALL
        self.author = '小鱼'

    def install_nodejs(self):
        wechat_version_dic = {1:"备份磁盘",2:"还原磁盘"}
        code,_ = ChooseTask(wechat_version_dic,"请选择操作:",False).run()
        if code==1:
            disk_origin = input('请输入你要备份的磁盘(默认:/dev/sda):')
            if not disk_origin:
                disk_origin = '/dev/sda'
            save_disk = input('请输入你要存放的文件磁盘(如:/dev/sdb2):')
            file_name = input('请输入文件名guidebot_240802:')
            CmdTask(f"mkdir -p /tmp/save_disk && mount {save_disk} /tmp/save_disk").run()
            PrintUtils.print_info("查看进度: watch -n 1 pkill -USR1 -x dd")
            command = f'cd /tmp/save_disk && dd if={disk_origin} | gzip > {file_name}.gz'
            CmdTask(command).run()
            
        else:
            pass
   
    def run(self):
        self.install_nodejs()

