# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_CONFIG
        self.name = "模板工程"
        self.author = '小鱼'
    def choose_pip_source(self):
        """选择pip源
        
        Returns:
            str: 选择的源URL
        """
        sources = {
            "清华源": "https://pypi.tuna.tsinghua.edu.cn/simple",
            "阿里云": "https://mirrors.aliyun.com/pypi/simple",
            "中国科学技术大学": "https://pypi.mirrors.ustc.edu.cn/simple",
            "华为云": "https://repo.huaweicloud.com/repository/pypi/simple"
        }
        
        # 构建选择字典
        choose_dict = {}
        i = 1
        for name, url in sources.items():
            choose_dict[i] = f"{name} - {url}"
            i += 1
        
        PrintUtils.print_info("请选择要使用的pip源:")
        choose_index, choose_content = ChooseTask(choose_dict, "请选择pip源:").run()
        
        if choose_index == 0:
            PrintUtils.print_info("未选择源，默认使用中国科学技术大学源")
            return sources["中国科学技术大学"]
        
        try:
            # choose_index 已经是整数，直接使用
            selected_name = list(sources.keys())[choose_index-1]
            return sources[selected_name]
        except (IndexError) as e:
            PrintUtils.print_error(f"选择源时出错: {str(e)}，使用中国科学技术大学源")
            return sources["中国科学技术大学"]

    def install_rosdepc(self):
        """
        安装rosdepc工具，用于ROS依赖管理
        """
        # 安装python3-pip
        pip_install_result = CmdTask("sudo apt install python3-pip -y", 0).run()
        if pip_install_result[0] != 0:
            PrintUtils.print_error("安装python3-pip失败")
            return False
        
        # 选择pip源
        selected_source = self.choose_pip_source()
        PrintUtils.print_success(f"您选择了: {selected_source}")
        
        # 先尝试不带参数安装rosdepc
        PrintUtils.print_info(f"正在使用 {selected_source} 安装 rosdepc...")
        cmd_ret = CmdTask(f"sudo pip3 install -i {selected_source} rosdepc").run()
        
        # 如果不带参数安装失败，尝试使用 --break-system-packages 参数安装
        if cmd_ret[0] != 0:
            PrintUtils.print_warn("安装失败，尝试使用 --break-system-packages 参数安装...")
            cmd_ret = CmdTask(f"sudo pip3 install -i {selected_source} rosdepc --break-system-packages").run()
            # 如果仍然失败，返回False
            if cmd_ret[0] != 0:
                PrintUtils.print_error("两种方式安装rosdepc均失败")
                return False
        
        # 初始化rosdepc
        init_result = CmdTask("sudo rosdepc init", 0).run()
        if init_result[0] != 0:
            PrintUtils.print_error("rosdepc初始化失败")
            return False
        
        # 修复权限问题
        fix_result = CmdTask("sudo rosdepc fix-permissions", 0).run()
        if fix_result[0] != 0:
            PrintUtils.print_error("修复rosdepc权限失败")
            return False
        
        PrintUtils.print_info('已为您安装好rosdepc,请使用:\nrosdepc update \n进行测试更新,最后欢迎关注微信公众号《鱼香ROS》')
        return True
    
    def run(self):
        """
        运行rosdepc安装工具
        
        Returns:
            bool: 安装成功返回True，失败返回False
        """
        # 正式的运行
        return self.install_rosdepc()