# 一键安装(忘记要Star了，点了再走哦~)

> ### 大家想要的工具可以在[心愿清单](https://github.com/fishros/install/issues/2)中提出,说不定会有魔法师满足你的心愿

## 工具列表

已支持工具列表（方括号里是菜单编号）：

**ROS安装**
- [1] 一键安装(推荐):ROS(小白/高手两种模式,自动识别系统并换源,支持ROS1/ROS2/树莓派/Jetson)  [贡献@小鱼](https://github.com/fishros)
- [11] 一键安装:ROS Docker版(支持所有版本ROS/ROS2,系统版本不匹配时使用)
- [16] 一键安装:系统自带ROS(仅供特殊情况下使用)

**ROS开发工具**
- [4] 一键配置:ROS环境(快速更新ROS环境设置,自动生成环境选择,修复中文路径编译报错)  [贡献@小鱼](https://github.com/fishros)
- [3] 一键安装:rosdepc(小鱼的国内版rosdep,又快又好用)  [贡献@小鱼](https://github.com/fishros)
- [22] 一键安装:ROS常用功能包(导航Nav2/建图slam_toolbox、Cartographer/键盘、手柄遥控等)
- [9] 一键安装:Cartographer(仅支持ROS1:Ubuntu16/18/20)  贡献 [@小鱼](https://github.com/fishros) & [@Catalpa](https://github.com/Y-zi)
- [12] 一键安装:MicroROS开发环境(PlatformIO,支持FishBot)

**换源与网络**
- [5] 一键配置:系统源(更换国内源,支持Ubuntu/Debian全版本)  [贡献@小鱼](https://github.com/fishros)
- [13] 一键配置:Python国内源
- [17] 一键配置:Docker代理(支持VPN+代理服务两种模式)
- [14] 一键安装:科学上网代理工具

**开发工具**
- [7] 一键安装:VSCode(支持amd64和arm64)  [贡献@小鱼](https://github.com/fishros)
- [8] 一键安装:Docker(支持amd64和arm64)  [贡献@alyssa](https://github.com/alyssa1024)
- [6] 一键安装:Node.js开发环境  [贡献@小鱼](https://github.com/fishros)
- [2] 一键安装:GitHub桌面版(小鱼常用的GitHub客户端)  [贡献@小鱼](https://github.com/fishros)
- [18] 一键安装/卸载:OpenCode(AI编程助手)

**日常软件**
- [10] 一键安装:微信客户端  [贡献@小鱼](https://github.com/fishros)
- [15] 一键安装:QQ for Linux

> 菜单编号固定不变（自动化配置按编号选择），新增工具只会用新编号。



## 使用方法
```
source <(wget -qO- http://fishros.com/install)
```

装 ROS 在菜单里输入 `1`，接着选安装模式：不知道怎么选的选 `1` 小白模式，确认后脚本会自动识别系统、
测速换源、挑选可用的镜像和对应的 ROS 版本，中途不用再做选择，装完会列出替你选了什么；
想自己指定镜像源和版本的选 `2` 高手模式。

### 用自己的服务器测试新版本

把仓库文件放到任意 HTTP 服务器上，把 `install` 第一行改成你的地址，然后在测试机上运行即可，
后续所有工具脚本都会从这个地址下载：

```
# 服务器上(仓库目录内)
sed -i "1s#.*#export FISHROS_URL=http://<服务器IP>:8080/#" install
python3 -m http.server 8080
# 测试机上
wget http://<服务器IP>:8080/install -O fishros && . fishros
```

## 如何自动选择(Dockerfile中使用)

目前一键安装支持从配置文件自动输入选项，你需要手动运行一次一键安装，使用完毕后会自动产生 `/tmp/fish_install.yaml`。

使用下面的指令将配置文件拷贝到当前终端即可。

```
cp /tmp/fish_install.yaml ./
```

### Dockerfile中使用

使用样例如下

```
RUN apt update \ 
    && apt install wget python3-yaml -y  \
    # 安装melodic
    && echo "chooses:\n" > fish_install.yaml \
    && echo "- {choose: 1, desc: '一键安装:ROS(支持ROS和ROS2,树莓派Jetson)'}\n" >> fish_install.yaml \
    && echo "- {choose: 1, desc: 更换源继续安装}\n" >> fish_install.yaml \
    && echo "- {choose: 2, desc: 清理三方源}\n" >> fish_install.yaml \
    && echo "- {choose: 1, desc: melodic(ROS1)}\n" >> fish_install.yaml \
    && echo "- {choose: 1, desc: melodic(ROS1)桌面版}\n" >> fish_install.yaml \
    && wget http://fishros.com/install  -O fishros && /bin/bash fishros \
    # 进行最后的清理
    && rm -rf /var/lib/apt/lists/*  /tmp/* /var/tmp/* \
    && apt-get clean && apt autoclean 
```
一键换源

```
FROM ubuntu:22.04

# 一键换源
RUN apt update \
    && apt install wget python3 python3-yaml -y python3-distro\
    && echo "chooses:\n" > fish_install.yaml \
    && echo "- {choose: 5, desc: '一键安装:ROS(支持ROS和ROS2,树莓派Jetson)'}\n" >> fish_install.yaml \
    && echo "- {choose: 2, desc: 更换源继续安装}\n" >> fish_install.yaml \
    && echo "- {choose: 1, desc: 清理三方源}\n" >> fish_install.yaml \
    && wget http://fishros.com/install  -O fishros && /bin/bash fishros \
    # 进行最后的清理
    && rm -rf fish_install.yaml \
    && rm -rf /var/lib/apt/lists/*  /tmp/* /var/tmp/* \
    && apt-get clean && apt autoclean 
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
        self.author = '小鱼'

    def run(self):
        #正式的运行
        pass
```

接着修改type、name、author

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
- 一键安装vscode [小鱼](https://github.com/fishros)
- 一键安装:Docker(支持amd64和arm64) [@alyssa](https://github.com/alyssa1024)


