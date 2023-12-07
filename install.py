# -*- coding: utf-8 -*-
import os

url_prefix = 'http://fishros.com/install/install1s/'

base_url = url_prefix+'tools/base.py'

INSTALL_ROS = 0  # 安装ROS相关
INSTALL_SOFTWARE = 1  # 安装软件
CONFIG_TOOL = 2  # 配置相关


tools_type_map = {
    INSTALL_ROS: "ROS相关",
    INSTALL_SOFTWARE: "常用软件",
    CONFIG_TOOL: "配置工具"
}


tools ={
    1: {'tip':'一键安装(推荐):ROS(支持ROS/ROS2,树莓派Jetson)',                 'type':INSTALL_ROS,     'tool':url_prefix+'tools/tool_install_ros.py' ,'dep':[4,5] },
    2: {'tip':'一键安装:github桌面版(小鱼常用的github客户端)',             'type':INSTALL_SOFTWARE,     'tool':url_prefix+'tools/tool_install_github_desktop.py' ,'dep':[] },
    4: {'tip':'一键配置:ROS环境(快速更新ROS环境设置,自动生成环境选择)',     'type':INSTALL_ROS,     'tool':url_prefix+'tools/tool_config_rosenv.py' ,'dep':[] },
    3: {'tip':'一键安装:rosdep(小鱼的rosdepc,又快又好用)',                 'type':INSTALL_ROS,    'tool':url_prefix+'tools/tool_config_rosdep.py' ,'dep':[] },
    5: {'tip':'一键配置:系统源(更换系统源,支持全版本Ubuntu系统)',           'type':CONFIG_TOOL,    'tool':url_prefix+'tools/tool_config_system_source.py' ,'dep':[1] },
    6: {'tip':'一键安装:NodeJS环境',      'type':INSTALL_SOFTWARE,     'tool':url_prefix+'tools/tool_install_nodejs.py' ,'dep':[] },
    7: {'tip':'一键安装:VsCode开发工具',      'type':INSTALL_SOFTWARE,     'tool':url_prefix+'tools/tool_install_vscode.py' ,'dep':[] },
    8: {'tip':'一键安装:Docker',      'type':INSTALL_SOFTWARE,     'tool':url_prefix+'tools/tool_install_docker.py' ,'dep':[] },
    9: {'tip':'一键安装:Cartographer(内测版易失败)',      'type':INSTALL_ROS,     'tool':url_prefix+'tools/tool_install_cartographer.py' ,'dep':[3] },
    10: {'tip':'一键安装:微信(可以在Linux上使用的微信)',      'type':INSTALL_SOFTWARE,     'tool':url_prefix+'tools/tool_install_wechat.py' ,'dep':[8] },
    21: {'tip':'一键安装:ROS Docker版(支持所有版本ROS/ROS2)',                'type':INSTALL_ROS,    'tool':url_prefix+'tools/tool_install_ros_with_docker.py' ,'dep':[7,8] },
    12: {'tip':'一键安装:PlateformIO MicroROS开发环境(支持Fishbot)',      'type':INSTALL_SOFTWARE,     'tool':url_prefix+'tools/tool_install_micros_fishbot_env.py' ,'dep':[] },
    13: {'tip':'一键配置:python国内源','type':CONFIG_TOOL,'tool':url_prefix+'tools/tool_config_python_source.py' ,'dep':[] },
    14: {'tip':'一键安装:科学上网代理工具','type':INSTALL_SOFTWARE,'tool':url_prefix+'tools/tool_install_proxy_tool.py' ,'dep':[8] },
    15: {'tip':'一键安装：QQ for Linux', 'type':INSTALL_SOFTWARE, 'tool': url_prefix+'tools/tool_install_qq.py', 'dep':[]},
    16: {'tip':'一键安装：系统自带ROS (22.04 及以上原生)'type':INSTALL_ROS, 'tool': url_prefix+'tools/tool_install_ros1_systemdefault.py', 'dep':[5]},
    # 77: {'tip':'测试模式:运行自定义工具测试'},
    }
# 


# 创建用于存储不同类型工具的字典
tool_categories = {}

# 遍历tools字典，根据type值进行分类
for tool_id, tool_info in tools.items():
    tool_type = tool_info['type']
    # 如果该类型还没有在字典中创建，则创建一个新的列表来存储该类型的工具
    if tool_type not in tool_categories:
        tool_categories[tool_type] = {}
    # 将工具信息添加到相应类型的列表中
    tool_categories[tool_type][tool_id]=tool_info


def main():
    # download base
    os.system("wget {} -O /tmp/fishinstall/{} --no-check-certificate".format(base_url,base_url.replace(url_prefix,'')))
    from tools.base import CmdTask,FileUtils,PrintUtils,ChooseTask,ChooseWithCategoriesTask
    from tools.base import encoding_utf8,osversion,osarch
    from tools.base import run_tool_file,download_tools
    from tools.base import config_helper
    # PrintUtils.print_delay(f"检测到你的系统版本信息为{osversion.get_codename()},{osarch}",0.001)
    # 使用量统计
    CmdTask("wget https://fishros.org.cn/forum/topic/1733 -O /tmp/t1733 -q && rm -rf /tmp/t1733").run()

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
======一键安装已开源，请放心使用：https://github.com/fishros/install =======
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
    # for tool_id in tools.keys(): choose_dic[tool_id]  = tools[tool_id]["tip"]
    code,result = ChooseWithCategoriesTask(tool_categories, tips="---众多工具，等君来用---",categories=tools_type_map).run()

    if code==0: PrintUtils().print_success("是觉得没有合胃口的菜吗？那快联系的小鱼增加菜单吧~")
    elif code==77: 
        code,result = ChooseTask(choose_dic, "请选择你要测试的程序:").run()
        if  code<0 and code>=77:  return False
        # CmdTask("cp tools/* /tmp/fishinstall/tools/").run
        print(tools[code]['tool'].replace(url_prefix,'').replace("/","."))
        run_tool_file(tools[code]['tool'].replace(url_prefix,'').replace("/","."))
    else: 
        download_tools(code,tools)
        run_tool_file(tools[code]['tool'].replace(url_prefix,'').replace("/","."))

    config_helper.gen_config_file()
    PrintUtils.print_delay("欢迎加入机器人学习交流QQ群：438144612(入群口令：一键安装)",0.1)
    PrintUtils.print_success("鱼香小铺正式开业，最低499可入手一台能建图会导航的移动机器人，淘宝搜店：鱼香ROS 或打开链接查看：https://item.taobao.com/item.htm?id=696573635888",0.001)
    PrintUtils.print_success("如在使用过程中遇到问题，请打开：https://fishros.org.cn/forum 进行反馈",0.001)

if __name__=='__main__':
    main()
