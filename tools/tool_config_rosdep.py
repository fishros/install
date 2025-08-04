# -*- coding: utf-8 -*-
import time
import http.client
from urllib.parse import urlparse
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_CONFIG
        self.name = "模板工程"
        self.author = '小鱼'
        
    def test_source_speed(self, url):
        """测试源的速度
        
        Args:
            url (str): 源的URL
            
        Returns:
            float: 响应时间（秒）
        """
        try:
            start_time = time.time()
            parsed_url = urlparse(url)
            conn = http.client.HTTPSConnection(parsed_url.netloc, timeout=5)
            conn.request("HEAD", parsed_url.path)
            resp = conn.getresponse()
            conn.close()
            end_time = time.time()
            return end_time - start_time
        except Exception as e:
            PrintUtils.print_error(f"测试源 {url} 失败: {str(e)}")
            return float('inf')  # 返回无穷大表示连接失败
    
    def choose_pip_source(self):
        """选择pip源
        
        Returns:
            str: 选择的源URL
        """
        sources = {
            "清华源": "https://pypi.tuna.tsinghua.edu.cn/simple",
            "阿里云": "https://mirrors.aliyun.com/pypi/simple",
            "中国科技大学": "https://pypi.mirrors.ustc.edu.cn/simple",
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
            PrintUtils.print_info("未选择源，默认使用中国科技大学源")
            return sources["中国科技大学"]
        
        try:
            # choose_index 已经是整数，直接使用
            selected_name = list(sources.keys())[choose_index-1]
            return sources[selected_name]
        except (IndexError) as e:
            PrintUtils.print_error(f"选择源时出错: {str(e)}，使用中国科技大学源")
            return sources["中国科技大学"]

    def install_rosdepc(self):
        CmdTask("sudo apt install python3-pip -y", 0).run()
        
        # 选择源
        selected_source = self.choose_pip_source()
        PrintUtils.print_success(f"您选择了: {selected_source}")
        
        # 直接使用 --break-system-packages 参数安装，避免第一次安装失败
        PrintUtils.print_info(f"正在使用 {selected_source} 安装 rosdepc...")
        cmd_ret = CmdTask(f"sudo pip3 install -i {selected_source} rosdepc --break-system-packages").run()
        if cmd_ret[0]!=0:
            # 如果安装失败，尝试不带参数安装
            PrintUtils.print_warning("安装失败，尝试使用其他方式安装...")
            cmd_ret = CmdTask(f"sudo pip3 install -i {selected_source} rosdepc").run()
        CmdTask("sudo rosdepc init", 0).run()
        CmdTask("sudo rosdepc fix-permissions", 0).run()
        PrintUtils.print_info('已为您安装好rosdepc,请使用:\nrosdepc update \n进行测试更新,最后欢迎关注微信公众号《鱼香ROS》')


    def run(self):
        #正式的运行
        self.install_rosdepc()