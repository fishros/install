# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装微信"
        self.type = BaseTool.TYPE_INSTALL
        self.autor = '小鱼'

    def install_wechat(self):
        run_tool_file('tools.tool_install_docker')
        user =  FileUtils.getusers()[0]
        name = 'wechat'
        inputs = 'fcitx'
        version_dic = {1:"ibus(系统默认)",2:"fcitx"}
        code,_ = ChooseTask(version_dic,"请选择系统输入法版本(如果不知道怎么选,请选1-ibus):",False).run()
        if code == 1: inputs='ibus'
        file_path = '/home/{}/docker/{}/WeChatFiles'.format(user,name)
        CmdTask('mkdir -p {}'.format(file_path),os_command=True).run()
        result = CmdTask('sudo docker run -d --name wechat --device /dev/snd --ipc="host"  -v /tmp/.X11-unix:/tmp/.X11-unix  \
        -v {}:/WeChatFiles  -e DISPLAY=unix$DISPLAY  -e XMODIFIERS=@im={}  -e QT_IM_MODULE={}  -e GTK_IM_MODULE={}  -e AUDIO_GID=`getent group audio | cut -d: -f3` bestwu/wechat'.format(file_path,inputs,inputs,inputs),
        os_command=False).run()

        if result[0] != 0: PrintUtils.print_error("失败了。。请到社区或群聊反馈:{}".format(result[1]+result[2]))

        PrintUtils.print_info("===========================================")
        PrintUtils.print_success("以为你安装完成wechat，稍后会弹窗登录")
        PrintUtils.print_info("=================后续使用指令=================")
        PrintUtils.print_success("微信启动指令：sudo docker start {}".format(name))
        PrintUtils.print_info("微信关闭指令：sudo docker stop {}".format(name))
        PrintUtils.print_info("强制重启指令：sudo docker restart {}".format(name))
        PrintUtils.print_error("删除微信指令：sudo docker rm {}".format(name))
        PrintUtils.print_info("=================文件存储位置================")
        PrintUtils.print_delay("微信所有文件已经放到目录：{}".format(file_path))

    def run(self):
        self.install_wechat()

# sudo docker run -d --name wechat1 --device /dev/snd --ipc="host"  -v /tmp/.X11-unix:/tmp/.X11-unix  -v $HOME/WeChatFiles:/WeChatFiles  -e DISPLAY=unix$DISPLAY  -e XMODIFIERS=@im=fcitx  -e QT_IM_MODULE=fcitx  -e GTK_IM_MODULE=fcitx  -e AUDIO_GID=`getent group audio | cut -d: -f3`  bestwu/wechat