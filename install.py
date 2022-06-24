# -*- coding: utf-8 -*-
import os

url_prefix = 'http://fishros.com/install/install1s/'

base_url = url_prefix+'tools/base.py'

tools ={
    1: {'tip':'一键安装:ROS(支持ROS和ROS2,树莓派Jetson)',                 'type':0,     'tool':url_prefix+'tools/tool_install_ros.py' ,'dep':[4,5] },
    11: {'tip':'一键安装:ROS+Docker(支持所有版本ROS/ROS2)',                'type':0,    'tool':url_prefix+'tools/tool_install_ros_with_docker.py' ,'dep':[7,8] },
    2: {'tip':'一键安装:github桌面版(小鱼常用的github客户端)',             'type':0,     'tool':url_prefix+'tools/tool_install_github_desktop.py' ,'dep':[] },
    3: {'tip':'一键配置:rosdep(小鱼的rosdepc,又快又好用)',                 'type':2,    'tool':url_prefix+'tools/tool_config_rosdep.py' ,'dep':[] },
    4: {'tip':'一键配置:ROS环境(快速更新ROS环境设置,自动生成环境选择)',     'type':2,     'tool':url_prefix+'tools/tool_config_rosenv.py' ,'dep':[] },
    5: {'tip':'一键配置:系统源(更换系统源,支持全版本Ubuntu系统)',           'type':2,    'tool':url_prefix+'tools/tool_config_system_source.py' ,'dep':[1] },
    6: {'tip':'一键安装:nodejs',      'type':0,     'tool':url_prefix+'tools/tool_install_nodejs.py' ,'dep':[] },
    7: {'tip':'一键安装:VsCode开发工具',      'type':0,     'tool':url_prefix+'tools/tool_install_vscode.py' ,'dep':[] },
    8: {'tip':'一键安装:Docker',      'type':0,     'tool':url_prefix+'tools/tool_install_docker.py' ,'dep':[] },
    9: {'tip':'一键安装:Cartographer(内测版v0.1)',      'type':0,     'tool':url_prefix+'tools/tool_install_cartographer.py' ,'dep':[3] },
    10: {'tip':'一键安装:微信(可以在Linux上使用的微信)',      'type':0,     'tool':url_prefix+'tools/tool_install_wechat.py' ,'dep':[8] },
    # 11: {'tip':'一键安装:Code-Server(网页版VsCode)',      'type':0,     'tool':url_prefix+'tools/tool_install_code_server.py' ,'dep':[] },
    77: {'tip':'测试模式:运行自定义工具测试'},
}
# 


def main():
    # download base
    os.system("wget {} -O /tmp/fishinstall/{} --no-check-certificate".format(base_url,base_url.replace(url_prefix,'')))
    from tools.base import CmdTask,FileUtils,PrintUtils,ChooseTask
    from tools.base import encoding_utf8,osversion,osarch
    from tools.base import run_tool_file,download_tools
    from tools.base import config_helper

    # check base config
    if not encoding_utf8:
        print("Your system encoding not support ,will install some packgaes..")
        CmdTask("sudo apt-get install language-pack-zh-hans -y",0).run()
        CmdTask("sudo apt-get install apt-transport-https -y",0).run()
        FileUtils.append("/etc/profile",'export LANG="zh_CN.UTF-8"')
        print('Finish! Please Try Again!')
        print('Solutions: https://fishros.org.cn/forum/topic/24 ')
        return False
    PrintUtils.print_success("基础检查通过...")

    book = """
                        .-~~~~~~~~~-._       _.-~~~~~~~~~-.
                    __.'              ~.   .~              `.__
                .'//     开卷有益        \./     书山有路     \\ `.
                .'// 可以多看看小鱼的文章   |    关注公众号鱼香ROS  \\ `.
            .'// .-~"""""""~~~~-._     |     _,-~~~~"""""""~-. \\`.
            .'//.-"                 `-.  |  .-'                 "-.\\`.
        .'//______.============-..   \ | /   ..-============.______\\`.
        .'______________________________\|/______________________________`
        ----------------------------------------------------------------------"""

    tip = """===============================================================================
======欢迎使用一键安装工具，人生苦短，三省吾身，省时省力省心!=======
======一键安装已开源，请放心使用：https://github.com/fishros/install=======
===============================================================================
    """
    end_tip = """===============================================================================
如果觉得工具好用,请给个star,如果你想和小鱼一起编写工具,请关注微信公众号<鱼香ROS>,联系小鱼
更多工具教程，请访问鱼香ROS官方网站:http://fishros.com
    """
    PrintUtils.print_delay(tip,0.001)
    PrintUtils.print_delay(book,0.001)

    # download tools
    choose_dic = {}
    for tool_id in tools.keys(): choose_dic[tool_id]  = tools[tool_id]["tip"]
    code,result = ChooseTask(choose_dic, "---众多工具，等君来用---").run()
    if code==0: PrintUtils().print_success("是觉得没有合胃口的菜吗？那快联系的小鱼增加菜单吧~")
    elif code==77: 
        code,result = ChooseTask(choose_dic, "请选择你要测试的程序:").run()
        if  code<0 and code>=77:  return False
        # CmdTask("cp tools/* /tmp/fishinstall/tools/").run
        run_tool_file(tools[code]['tool'].replace(url_prefix,'').replace("/","."))
         
    else: 
        download_tools(code,tools)
        run_tool_file(tools[code]['tool'].replace(url_prefix,'').replace("/","."))

    config_helper.gen_config_file()
    PrintUtils.print_delay("欢迎加入机器人学习交流QQ群：139707339(入群口令：一键安装)",0.1)
    PrintUtils.print_success("如在使用过程中遇到问题，请打开：https://fishros.org.cn/forum 进行反馈",0.001)

if __name__=='__main__':
    main()