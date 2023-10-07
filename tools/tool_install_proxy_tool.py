# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion,osarch
from .base import run_tool_file

#

start_clash_sh = """export CLASH_SERVER="{server_url}"
cd {clash_home}
export http_proxy=''
export https_proxy=''
mkdir -p $HOME/.config/clash
wget $CLASH_SERVER -O $HOME/.config/clash/config.yaml
#sed -i 's/127.0.0.1:9090/0.0.0.0:9090/g'  $HOME/.config/clash/config.yaml
sed -i 's/allow-lan: false/allow-lan: true/g'  $HOME/.config/clash/config.yaml
file_url="http://github.fishros.org/https://github.com/Dreamacro/maxmind-geoip/releases/download/20230912/Country.mmdb"
target_dir="$HOME/.config/clash/"
# 检查文件是否存在
if [ ! -e "${target_dir}Country.mmdb" ]; then
    # 如果文件不存在，则使用wget下载文件
    wget -O "${target_dir}Country.mmdb" "$file_url"
    if [ $? -eq 0 ]; then
        echo "文件下载成功。"
    else
        echo "文件下载失败。"
        exit 1
    fi
else
    echo "文件已存在，无需下载。"
fi
xdg-open http://fishros.org:1234/ >> /dev/null &
sleep 3
echo "==============================================="
echo "终端通过环境变量设置: export http_proxy=http://127.0.0.1:7890 && export https_proxy=http://127.0.0.1:7890"
echo "配置系统默认代理方式: 系统设置->网络->网络代理->手动->HTTP(127.0.0.1 7890)->HTTPS(127.0.0.1 7890)"
echo "管理页面方法：https://fishros.org.cn/forum/topic/668 "
echo "=============================================="
./clash
"""

start_clash_desktop ="""[Desktop Entry]
Type=Application
Exec=gnome-terminal -e "/bin/bash {script_path}"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[zh_CN]=启动代理
Name=clash
Comment[zh_CN]=
Comment=
"""

start_clash_new_terminal_desktop ="""[Desktop Entry]
Type=Application
Exec=gnome-terminal -e "/bin/bash {script_path}"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[zh_CN]=启动代理
Name=clash
Comment[zh_CN]=
Comment=
"""

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装 Linux 代理科学上网工具"
        self.type = BaseTool.TYPE_INSTALL
        self.autor = '小鱼'

    def install_proxy_tool(self):
        PrintUtils.print_info("开始根据系统架构,为你下载对应版本的clash~")
        # 根据系统架构下载不同版本的安装包
        user_home = FileUtils.getusershome()[0]
        clash_home = "{}.clash/".format(user_home)
        CmdTask("mkdir -p {}".format(clash_home),os_command=True).run()
        if osarch=='amd64':
            CmdTask('sudo wget http://github.fishros.org/https://github.com/Dreamacro/clash/releases/download/v1.17.0/clash-linux-amd64-v1.17.0.gz -O {}clash.gz'.format(clash_home),os_command=True).run()
        elif osarch=='arm64':
            CmdTask('sudo wget http://github.fishros.org/https://github.com/Dreamacro/clash/releases/download/v1.17.0/clash-linux-arm64-v1.17.0.gz -O {}clash.gz'.format(clash_home),os_command=True).run()
        else:
            return False
        PrintUtils.print_info("下载完成,接下来为你解压Clash~")
        CmdTask('sudo rm -rf {}clash'.format(clash_home),os_command=True).run()
        CmdTask('gzip -d {}.clash/clash.gz'.format(user_home),path=clash_home.format(user_home),os_command=True).run()
        CmdTask('sudo chmod a+x {}.clash/clash'.format(user_home),os_command=True).run()

        PrintUtils.print_warn("请输入CLASH订阅地址(若无请访问:https://fishros.org.cn/forum/topic/668 获取)")
        serve_url = input("订阅地址:")

        PrintUtils.print_info("正在配置启动脚本....")
        FileUtils.new(path=clash_home,name="start_clash.sh",data=start_clash_sh.replace("{clash_home}",clash_home).replace("{server_url}",serve_url))
        CmdTask('sudo chmod a+x {}start_clash.sh'.format(clash_home),os_command=True).run()
        PrintUtils.print_info("启动脚本配置完成，你可以在目录: {}  运行 start_clash.sh 启动工具，启动后可通过网页：http://fishros.org:1234/ 进行管理".format(clash_home))

        PrintUtils.print_info("==========进行启动项配置...===========")
        dic = {1:"设置开机自启动",2:"不设置开机自启动"}
        code,result = ChooseTask(dic, "是否设置为开机自启动?").run()
        auto_start_path = "{}.config/autostart/".format(user_home)
        if code==2: FileUtils.delete(auto_start_path+"start_clash.desktop")
        if code==1: 
            FileUtils.new(path=auto_start_path,name="start_clash.desktop",data=start_clash_desktop.replace("{script_path}",clash_home+"start_clash.sh"))
            CmdTask('sudo chmod a+x {}start_clash.desktop'.format(auto_start_path),os_command=True).run()

        PrintUtils.print_info("==========进行桌面快捷方式配置...===========")
        dic = {1:"添加桌面快捷方式",2:"不添加桌面快捷方式"}
        code,result = ChooseTask(dic, "是否添加桌面快捷方式?").run()
        if code==1:
            if FileUtils.exists("{}桌面".format(user_home)):
                desktop_path = "{}桌面/".format(user_home)
            if FileUtils.exists("{}Desktop".format(user_home)):
                desktop_path = "{}Desktop/".format(user_home)
            FileUtils.new(path=desktop_path,name="启动代理.desktop",data=start_clash_new_terminal_desktop.replace("{script_path}",clash_home+"start_clash.sh"))
            CmdTask('sudo chmod a+x {}启动代理.desktop'.format(desktop_path),os_command=True).run()
        
        PrintUtils.print_delay("==========使用方法===========")
        PrintUtils.print_delay("1.桌面快捷方式：需要先右击允许执行才能使用")
        PrintUtils.print_delay("2.可以在终端中直接运行脚本启动,直接输入:$HOME/.clash/start_clash.sh")
        PrintUtils.print_delay("3.终端通过环境变量设置: export http_proxy=http://127.0.0.1:7890 && export https_proxy=http://127.0.0.1:7890")
        PrintUtils.print_delay("4.配置系统默认代理方式: 系统设置->网络->网络代理->手动->HTTP(127.0.0.1 7890)->HTTPS(127.0.0.1 7890)")
        PrintUtils.print_delay("5.其他系统（Android/IOS/Windows/MacOS）下载软件:https://repo.trojan-cdn.com/")
        
    def run(self):
        self.install_proxy_tool()

