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

    def get_wechat_scripts(self,name,build):
        return """xhost +local: >> /dev/null
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
        # 桌面版微信
        git clone https://gitee.com/ohhuo/wechat_deb.git /tmp/wechaet_deb
        cd /tmp/wechaet_deb && cat wechat_* > wechat.deb 
        cd /tmp/wechaet_deb && sudo dpkg -i wechat.deb
        rm -rf /tmp/wechaet_deb 
        # https://fishros.org.cn/forum/topic/195
        # sudo apt remove wechat-linux-spark

        """
        wechat_version_dic = {1:"Docker版本",2:"桌面版本"}
        code,_ = ChooseTask(wechat_version_dic,"请选择微信版本(两个版本区别对比:https://fishros.org.cn/forum/topic/195):",False).run()
        if code==2:
            AptUtils.install_pkg("git")
            CmdTask('sudo apt install git',os_command=True).run()
            CmdTask('git clone https://gitee.com/ohhuo/wechat_deb.git /tmp/wechaet_deb',os_command=True).run()
            CmdTask('cd /tmp/wechaet_deb && cat wechat_* > wechat.deb',os_command=True).run()
            CmdTask('cd /tmp/wechaet_deb && sudo dpkg -i wechat.deb',os_command=True).run()
            CmdTask('rm -rf /tmp/wechaet_deb',os_command=True).run()
            PrintUtils.print_success("已为你安装完成wechat~")
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
            result = CmdTask(build,
            os_command=False).run()

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


    def run(self):
        self.install_wechat()

# sudo docker run -d --name wechat1 --device /dev/snd --ipc="host"  -v /tmp/.X11-unix:/tmp/.X11-unix  -v $HOME/WeChatFiles:/WeChatFiles  -e DISPLAY=unix$DISPLAY  -e XMODIFIERS=@im=fcitx  -e QT_IM_MODULE=fcitx  -e GTK_IM_MODULE=fcitx  -e AUDIO_GID=`getent group audio | cut -d: -f3`  bestwu/wechat