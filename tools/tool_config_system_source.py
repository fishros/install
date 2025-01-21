# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file



ubuntu_ports_sources_template = """
deb <sources>/ <code-name> main restricted universe multiverse
deb <sources>/ <code-name>-updates main restricted universe multiverse
deb <sources>/ <code-name>-backports main restricted universe multiverse
deb <sources>/ <code-name>-security main restricted universe multiverse
"""
ubuntu_amd64_sources_template = """
deb <sources>/ <code-name> main restricted universe multiverse
deb <sources>/ <code-name>-updates main restricted universe multiverse
deb <sources>/ <code-name>-backports main restricted universe multiverse
deb <sources>/ <code-name>-security main restricted universe multiverse
"""
debian_amd64_sources_template = """
deb <sources>/ <code-name> main contrib non-free
deb <sources>/ <code-name>-updates main contrib non-free
deb <sources>/ <code-name>-backports main contrib non-free
deb <sources>-security <code-name>/updates main contrib non-free
"""
ubuntu_ports_deb822_template = """
Types: deb
URIs: <sources>/
Suites: <code-name> <code-name>-updates <code-name>-backports
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

Types: deb
URIs: <sources>/
Suites: <code-name>-security
Components: main universe restricted multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
"""
ubuntu_amd64_deb822_template = """
Types: deb
URIs: <sources>/
Suites: <code-name> <code-name>-updates <code-name>-backports
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

# 以下安全更新软件源包含了官方源与镜像站配置，如有需要可自行修改注释切换
Types: deb
URIs: <sources>/
Suites: <code-name>-security
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
"""


class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_CONFIG
        self.name = "一键更换系统源"
        self.author = '小鱼'


    def add_ros_source(self):
        """快速添加ROS源"""
        dic = {1:"添加ROS/ROS2源",2:"不添加ROS/ROS2源"}
        code,result = ChooseTask(dic, "请问是否添加ROS和ROS2源？").run()
        if code==2: return
        tool = run_tool_file('tools.tool_install_ros',authorun=False)
        if not tool.support_install(): return False
        tool.add_key()
        tool.add_source()

    def clean_old_source(self):
        dic = {1:"仅更换系统源",2:"更换系统源并清理第三方源"}
        code,result = ChooseTask(dic, "请选择换源方式,如果不知道选什么请选2").run()
        FileUtils.delete('/etc/apt/sources.list')
        if code==2: 
            print("删除一个资源文件")
            FileUtils.delete('/etc/apt/sources.list.d')
            # fix add source failed before config system source 
            CmdTask('sudo mkdir -p /etc/apt/sources.list.d').run()



    def get_source_by_system(self,system,codename,arch,failed_sources=[]):
        # 实际测试发现，阿里云虽然延时很低，但是带宽也低的离谱，一点都不用心，删掉了
        ubuntu_amd64_sources = [
            "https://mirrors.tuna.tsinghua.edu.cn/ubuntu",
            # "https://mirrors.aliyun.com/ubuntu",
            # "https://mirrors.163.com/ubuntu",
            "https://mirrors.ustc.edu.cn/ubuntu",
            "https://archive.ubuntu.com/ubuntu",
            "https://mirrors.kernel.org/ubuntu",
            "http://mirrors.tuna.tsinghua.edu.cn/ubuntu",
            # "http://mirrors.aliyun.com/ubuntu",
            # "http://mirrors.163.com/ubuntu",
            "http://mirrors.ustc.edu.cn/ubuntu",
            "http://archive.ubuntu.com/ubuntu",
            "http://mirrors.kernel.org/ubuntu",
        ]
        ubuntu_ports_sources = [
            "https://ports.ubuntu.com/ubuntu-ports",
            # "https://mirrors.aliyun.com/ubuntu-ports",
            "https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports",
            "https://ports.ubuntu.com/ubuntu-ports",
            # "https://mirrors.aliyun.com/ubuntu-ports",
            "https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports",
             "http://ports.ubuntu.com/ubuntu-ports",
            # "https://mirrors.aliyun.com/ubuntu-ports",
            "http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports",
            "http://ports.ubuntu.com/ubuntu-ports",
            # "https://mirrors.aliyun.com/ubuntu-ports",
            "http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports",
        ]
        debian_amd64_sources = [
            "https://mirrors.tuna.tsinghua.edu.cn/debian",
            "https://mirrors.aliyun.com/debian",
            # "https://mirrors.163.com/debian",
            "https://mirrors.ustc.edu.cn/debian",
            "https://deb.debian.org/debian",
            "https://mirrors.kernel.org/debian",
            "http://mirrors.tuna.tsinghua.edu.cn/debian",
            "http://mirrors.aliyun.com/debian",
            # "http://mirrors.163.com/debian",
            "http://mirrors.ustc.edu.cn/debian",
            "http://deb.debian.org/debian",
            "http://mirrors.kernel.org/debian",
        ]
        sources = []
        template = ubuntu_amd64_sources_template
        if system=='ubuntu':
            if arch=='amd64':
                sources = ubuntu_amd64_sources
                template = ubuntu_amd64_sources_template
            else:
                sources = ubuntu_ports_sources
                template = ubuntu_ports_sources_template
        elif system=='debian':
            if arch=='amd64':
                template = debian_amd64_sources_template
                sources = debian_amd64_sources
        PrintUtils.print_delay('搜索到可用源:{}'.format(sources),0.002)
        PrintUtils.print_delay('接下来将进行自动测速以为您选择最快的源:')
        fast_source = AptUtils.get_fast_url(sources)
        
        if len(failed_sources)>0:
            PrintUtils.print_warn('接下来为您排除已经失败的源')
            for source in fast_source:
                if source in failed_sources:
                    PrintUtils.print_info('{} 已经测试失败，跳过!'.format(source))
                else:
                    return source,template
        else:
            return fast_source[0],template
        return None,None


    def replace_source(self,failed_sources=[]):
        arch = AptUtils.getArch()
        name = osversion.get_name()
        codename = osversion.get_codename()
        if name.find("ubuntu")>=0:
            system = 'ubuntu'
        elif name.find("debian")>=0:
            system = 'debian'
        else:
            return None
        PrintUtils.print_delay('检测到当前系统:{} 架构:{} 代号:{},正在为你搜索适合的源...'.format(system,arch,codename))
        source,template =  self.get_source_by_system(system,codename,arch,failed_sources)
        if not source: return None
        PrintUtils.print_success('为您选择最快镜像源:{}'.format(source))
        FileUtils.new('/etc/apt/','sources.list',template.replace("<code-name>",codename).replace('<sources>',source))
        return source
        

    def change_sys_source(self):
        self.clean_old_source()

        failed_sources = []
        source = self.replace_source(failed_sources)
        if source:
            PrintUtils.print_delay("替换镜像源完成，尝试进行更新....")
            result = CmdTask('sudo apt update',100).run()
            while result[0]!= 0:
                failed_sources.append(source)
                PrintUtils.print_warn("更新失败，尝试更换其他源")
                source = self.replace_source(failed_sources)
                result = CmdTask('sudo apt update',100).run()
        else:
            PrintUtils.print_error("没有找到合适的镜像源,臣妾告退!")

#         # update
#         PrintUtils.print_delay("替换完成，尝试第一次更新....")
#         result = CmdTask('sudo apt update',100).run()
#         # https error update second
#         if result[0]!= 0 and FileUtils.check_result(result[1]+result[2],['Certificate verification','证书']):
#             PrintUtils.print_delay("发生证书错误，尝试第二次更新....")
#             FileUtils.delete('/etc/apt/sources.list')
#             FileUtils.new('/etc/apt/','sources.list',source.replace("https://","http://").replace("<code-name>",osversion.get_codename()))
#             result = CmdTask('sudo apt update',100).run()
#         if result[0]!=0:
#             PrintUtils.print_info("更新失败，开始更换导入方式并三次尝试...")
#             result = CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 0E98404D386FA1D9",10).run()
#             result = CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys DCC9EFBF77E11517",10).run()
#             result = CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 54404762BBB6E853",10).run()
#             result = CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F42ED6FBAB17C654",10).run()
#             # sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 
#             # result = CmdTask("apt-get install debian-keyring debian-archive-keyring",10).run()
#             result = CmdTask("apt-key update",10).run()
#             result = CmdTask('sudo apt update',100).run()
#         if result[0]!=0:
#             PrintUtils.print_info("""如果出现问题NO_PUBKEY XXXXXXXX，请手动运行添加指令：apt-key adv --keyserver keyserver.ubuntu.com --recv-keys XXXXXXXX
# 如：error： NO_PUBKEY 0E98404D386FA1D9
# 运行指令：sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 0E98404D386FA1D9
#             """)
#         # final check

        if result[0]==0: 
            PrintUtils.print_success("搞定了,不信你看,累死宝宝了，还不快去给小鱼点个赞~")
            PrintUtils.print_info(result[1])
        PrintUtils.print_success("镜像更新完成.....")

    def run(self):
        # 正式的运行
        self.change_sys_source()
        # 添加 ROS Source
        self.add_ros_source()