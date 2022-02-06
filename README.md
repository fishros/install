# 一键安装

## 工具列表

已支持工具列表：

- 一键安装:ROS(支持ROS和ROS2,树莓派Jetson)  [贡献@小鱼](https://github.com/fishros)
- 一键安装:github桌面版(小鱼常用的github客户端)  [贡献@小鱼](https://github.com/fishros)
- 一键安装:nodejs开发环境(通过nodejs可以预览小鱼官网噢  [贡献@小鱼](https://github.com/fishros)
- 一键配置:rosdep(小鱼的rosdepc,又快又好用)  [贡献@小鱼](https://github.com/fishros)
- 一键配置:ROS环境(快速更新ROS环境设置,自动生成环境选择)  [贡献@小鱼](https://github.com/fishros)
- 一键配置:系统源(更换系统源,支持全版本Ubuntu系统)  [贡献@小鱼](https://github.com/fishros)

可以参考的待添加工具：

- 一键安装VsCode


## 使用方法
```
wget http://fishros.com/install -O fishros && . fishros
```


## 贡献指南

如果想把自己的常用安装程序变成一键安装程序，可以遵循下面的贡献指南。

### 1.fork工程

fork工程到你的github,然后克隆工程到本地

### 2.新建文件

在本地的工程的tools目录下新建py文件

- 若是安装工具命名为：tool_install_xxx.py
- 若是配置工具为：tool_config_xxx.py

### 3.编写程序

拷贝模板到你新建的文件：

```
# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils,CmdTask,FileUtils,AptUtils,ChooseTask
from .base import osversion
from .base import run_tool_file

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_INSTALL
        self.name = "模板工程"
        self.autor = '小鱼'

    def run(self):
        #正式的运行
        pass
```

接着修改type、name、autor

在run函数中编写逻辑，可以提供给你的工具有：
1. PrintUtils 打印文字
2. FileUtils 操作文件
3. AptUtils 操作Apt
4. ChooseTask 选择选项
5. CmdTask 运行命令行工具
6. run_tool_file 运行其他工具（需要在install.py的tools中配置dep）

信息：
1. osversion 系统相关信息
2. osarch 架构信息 amd64/i386/arm

### 4.在install.py中tools中添加一条信息

### 5.运行测试


## 贡献名单

- 一键安装ROS [小鱼](https://github.com/fishros)
- 一键安装github-deskto [小鱼](https://github.com/fishros)
- 一键配置rosdep [小鱼](https://github.com/fishros)
- 一键配置ros环境 [小鱼](https://github.com/fishros)
- 一键配置系统源 [小鱼](https://github.com/fishros)
- 一键安装nodejs [小鱼](https://github.com/fishros)