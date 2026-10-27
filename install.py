# -*- coding: utf-8 -*-
import os
import importlib

url_prefix = os.environ.get("FISHROS_URL", "http://mirror.fishros.com/install/")
base_url = os.path.join(url_prefix, "tools/base.py")
translator_url = os.path.join(url_prefix, "tools/translation/translator.py")

# 菜单分组, 显示顺序与下面 tools_type_map 的书写顺序一致
CAT_ROS_INSTALL = 0
CAT_ROS_TOOLS = 1
CAT_SOURCE_NETWORK = 2
CAT_DEV_TOOLS = 3
CAT_DAILY = 4

tools_type_map = {
    CAT_ROS_INSTALL: "ROS安装",
    CAT_ROS_TOOLS: "ROS开发工具",
    CAT_SOURCE_NETWORK: "换源与网络",
    CAT_DEV_TOOLS: "开发工具",
    CAT_DAILY: "日常软件",
}

# 菜单编号是对外接口(fish_install.yaml / Dockerfile 里按编号自动选择), 只能新增不能改号;
# 菜单里按本字典的书写顺序展示, 所以调整顺序只需要挪位置, 不要改编号
tools = {
    # ---------------- ROS安装 ----------------
    # 小白模式已并入菜单 1, 这里只保留条目供菜单 1 下载依赖, 不在菜单里展示
    21: {
        "tip": "一键安装:ROS全自动版(新手推荐,自动识别系统/换源/选版本,只需确认一次)",
        "type": CAT_ROS_INSTALL,
        "tool": "tools/tool_install_ros_auto.py",
        "dep": [1, 4, 5],
        "hidden": True,
    },
    1: {
        "tip": "一键安装(推荐):ROS(小白/高手两种模式,自动识别系统并换源,支持ROS1/ROS2/树莓派/Jetson)",
        "type": CAT_ROS_INSTALL,
        "tool": "tools/tool_install_ros.py",
        "dep": [4, 5, 21],
    },
    11: {
        "tip": "一键安装:ROS Docker版(支持所有版本ROS/ROS2,系统版本不匹配时使用)",
        "type": CAT_ROS_INSTALL,
        "tool": "tools/tool_install_ros_with_docker.py",
        "dep": [7, 8],
    },
    16: {
        "tip": "一键安装:系统自带ROS(！！警告！！仅供特殊情况下使用)",
        "type": CAT_ROS_INSTALL,
        "tool": "tools/tool_install_ros1_systemdefault.py",
        "dep": [5],
    },
    # ---------------- ROS开发工具 ----------------
    4: {
        "tip": "一键配置:ROS环境(快速更新ROS环境设置,自动生成环境选择,修复中文路径编译报错)",
        "type": CAT_ROS_TOOLS,
        "tool": "tools/tool_config_rosenv.py",
        "dep": [],
    },
    3: {
        "tip": "一键安装:rosdepc(小鱼的国内版rosdep,又快又好用)",
        "type": CAT_ROS_TOOLS,
        "tool": "tools/tool_config_rosdep.py",
        "dep": [],
    },
    22: {
        "tip": "一键安装:ROS常用功能包(导航Nav2/建图slam_toolbox、Cartographer/键盘、手柄遥控等)",
        "type": CAT_ROS_TOOLS,
        "tool": "tools/tool_install_ros_pkgs.py",
        "dep": [1],
    },
    9: {
        "tip": "一键安装:Cartographer(谷歌建图算法,仅支持ROS1:Ubuntu16/18/20)",
        "type": CAT_ROS_TOOLS,
        "tool": "tools/tool_install_cartographer.py",
        "dep": [3],
    },
    12: {
        "tip": "一键安装:MicroROS开发环境(PlatformIO,支持FishBot)",
        "type": CAT_ROS_TOOLS,
        "tool": "tools/tool_install_micros_fishbot_env.py",
        "dep": [],
    },
    # ---------------- 换源与网络 ----------------
    5: {
        "tip": "一键配置:系统源(更换国内源,支持Ubuntu/Debian全版本)",
        "type": CAT_SOURCE_NETWORK,
        "tool": "tools/tool_config_system_source.py",
        "dep": [1],
    },
    13: {
        "tip": "一键配置:Python国内源(加速pip安装)",
        "type": CAT_SOURCE_NETWORK,
        "tool": "tools/tool_config_python_source.py",
        "dep": [],
    },
    17: {
        "tip": "一键配置:Docker代理(支持VPN+代理服务两种模式)",
        "type": CAT_SOURCE_NETWORK,
        "tool": "tools/tool_config_docker_proxy.py",
        "dep": [],
    },
    14: {
        "tip": "一键安装:科学上网代理工具",
        "type": CAT_SOURCE_NETWORK,
        "tool": "tools/tool_install_proxy_tool.py",
        "dep": [8],
    },
    # ---------------- 开发工具 ----------------
    7: {
        "tip": "一键安装:VSCode(代码编辑器)",
        "type": CAT_DEV_TOOLS,
        "tool": "tools/tool_install_vscode.py",
        "dep": [],
    },
    8: {
        "tip": "一键安装:Docker",
        "type": CAT_DEV_TOOLS,
        "tool": "tools/tool_install_docker.py",
        "dep": [],
    },
    6: {
        "tip": "一键安装:Node.js环境",
        "type": CAT_DEV_TOOLS,
        "tool": "tools/tool_install_nodejs.py",
        "dep": [],
    },
    2: {
        "tip": "一键安装:GitHub桌面版(小鱼常用的GitHub客户端)",
        "type": CAT_DEV_TOOLS,
        "tool": "tools/tool_install_github_desktop.py",
        "dep": [],
    },
    18: {
        "tip": "一键安装/卸载:OpenCode(AI编程助手)",
        "type": CAT_DEV_TOOLS,
        "tool": "tools/tool_install_opencode.py",
        "dep": [6],
    },
    # 19: {
    #     "tip": "一键清理:OpenClaw(可选保留配置)",
    #     "type": CAT_DEV_TOOLS,
    #     "tool": "tools/tool_config_openclaw_cleanup.py",
    #     "dep": [],
    # },
    # 20: {
    #     "tip": "一键安装:OpenClaw(智能AI助手)",
    #     "type": CAT_DEV_TOOLS,
    #     "tool": "tools/tool_install_openclaw.py",
    #     "dep": [6],
    # },
    # ---------------- 日常软件 ----------------
    10: {
        "tip": "一键安装:微信(可以在Linux上使用的微信)",
        "type": CAT_DAILY,
        "tool": "tools/tool_install_wechat.py",
        "dep": [8],
    },
    15: {
        "tip": "一键安装:QQ for Linux",
        "type": CAT_DAILY,
        "tool": "tools/tool_install_qq.py",
        "dep": [],
    },
}


# 创建用于存储不同类型工具的字典，按目录顺序展示
tool_categories = {tool_type: {} for tool_type in tools_type_map}

# 遍历tools字典，根据type值进行分类
for tool_id, tool_info in tools.items():
    if tool_info.get("hidden"):
        continue
    tool_type = tool_info["type"]
    tool_categories[tool_type][tool_id] = tool_info

# 清理空目录，避免展示无工具分类
tool_categories = {k: v for k, v in tool_categories.items() if v}

tracking = None


def main():
    os.system("mkdir -p /tmp/fishinstall/tools/translation/assets")
    url_prefix = os.environ.get("FISHROS_URL", "http://mirror.fishros.com/install/")
    if url_prefix:
        os.system(
            "wget {} -O /tmp/fishinstall/{} --no-check-certificate".format(
                base_url, base_url.replace(url_prefix, "")
            )
        )
        os.system(
            "wget {} -O /tmp/fishinstall/{} --no-check-certificate".format(
                translator_url, translator_url.replace(url_prefix, "")
            )
        )

    from tools.base import (
        CmdTask,
        FileUtils,
        PrintUtils,
        ChooseTask,
        ChooseWithCategoriesTask,
        Tracking,
        AdUtils,
        BaseTool,
    )
    from tools.base import encoding_utf8, osversion, osarch
    from tools.base import run_tool_file, download_tools
    from tools.base import config_helper, tr

    importlib.import_module("tools.translation.translator").Linguist()
    from tools.base import tr
    import copy

    global tracing
    tracing = copy.copy(Tracking)

    # 使用量统计
    CmdTask(
        "wget https://fishros.org.cn/forum/topic/1733 -O /tmp/t1733 -q --no-check-certificate --timeout 10 && rm -rf /tmp/t1733"
    ).run()

    PrintUtils.print_success(tr.tr("已为您切换语言至当前所在国家语言:") + tr.lang)
    # 只有使用官方镜像站时才切到 GitHub; 自建服务器(FISHROS_URL 指向别处)测试时保持原地址
    if tr.country != "CN" and "mirror.fishros.com" in url_prefix:
        PrintUtils.print_success(
            tr.tr(
                "检测到当前不在CN,切换服务地址为:https://raw.githubusercontent.com/fishros/install/master/"
            )
        )
        url_prefix = "https://raw.githubusercontent.com/fishros/install/master/"

    # check base config
    if not encoding_utf8:
        print("Your system encoding not support ,will install some packgaes..")
        CmdTask("sudo apt-get install language-pack-zh-hans -y", 0).run()
        CmdTask("sudo apt-get install apt-transport-https -y", 0).run()
        FileUtils.append("/etc/profile", 'export LANG="zh_CN.UTF-8"')
        print("Finish! Please Try Again!")
        print("Solutions: https://fishros.org.cn/forum/topic/24 ")
        return False
    PrintUtils.print_success(tr.tr("基础检查通过..."))

    book = tr.tr("""
                        .-~~~~~~~~~-._       _.-~~~~~~~~~-.
                    __.'              ~.   .~              `.__
                .'//     开卷有益        \./     书山有路     \\ `.
                .'// 可以多看看小鱼的文章  | 关注B站鱼香ROS机器人 \\ `.
            .'// .-~~~~~~~~~~~~~~-._     |     _,-~~~~~~~~~~~. \\`.
            .'//.-"                 `-.  |  .-'                 "-.\\`.
        .'//______.============-..   \ | /   ..-============.______\\`.
        .'______________________________\|/______________________________`
        ----------------------------------------------------------------------""")

    tip = tr.tr("""===============================================================================
======欢迎使用一键安装工具，人生苦短，三省吾身，省时省力省心!=======
======一键安装已开源，请放心使用：https://github.com/fishros/install =======
===============================================================================
    """)
    end_tip = tr.tr("""===============================================================================
如果觉得工具好用,请给个star,如果你想和小鱼一起编写工具,请关注B站/公众号<鱼香ROS>,联系小鱼
更多工具教程，请访问鱼香ROS官方网站:http://fishros.com
    """)
    PrintUtils.print_delay(tip, 0.001)
    PrintUtils.print_delay(book, 0.001)
    # download tools
    while True:
        code, result = ChooseWithCategoriesTask(
            tool_categories,
            tips=tr.tr("---众多工具，等君来用---"),
            categories=tools_type_map,
        ).run()
        if code == 0:
            PrintUtils().print_success(
                tr.tr("是觉得没有合胃口的菜吗？那快联系的小鱼增加菜单吧~")
            )
            break
        if url_prefix:
            download_tools(code, tools, url_prefix)
        ChooseTask.last_back = False
        ret = run_tool_file(tools[code]["tool"].replace("/", "."))
        # 在工具里选了 [0] 返回上一步退出来的, 回到主菜单重新选
        if ret == BaseTool.BACK or ChooseTask.last_back:
            PrintUtils.print_info(tr.tr("已返回主菜单"))
            continue
        if ret == False:
            AdUtils.mark_failed()
        break

    # 检查是否在 GitHub Actions 环境中运行或使用了测试配置文件
    # 如果是，则跳过生成配置文件和后续的打印操作，因为这些操作需要用户输入
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        and os.environ.get("FISH_INSTALL_CONFIG") is None
    ):
        config_helper.gen_config_file()
        # 推广内容从服务器的 ads.json 读取, 见 tools/base.py 的 AdUtils
        AdUtils.show("finish_shop")
        AdUtils.show("finish")


def ensure_utf8():
    """
    终端编码不是 UTF-8(LANG 没设置、GBK 等)时, 打印中文会出错. 原来的做法是装中文语言包后让用户重跑,
    但语言包没生效时就会一直提示 Finish! Please Try Again!(社区帖 24).
    改为直接用系统自带的 C.UTF-8 重新启动自己; 重启后仍不是 UTF-8 才走原来的语言包流程
    """
    import locale
    import sys

    if "UTF" in locale.getpreferredencoding().upper() or os.environ.get("FISHROS_UTF8_RESTARTED"):
        return
    print("Terminal encoding is not UTF-8, restarting with C.UTF-8 ...")
    sys.stdout.flush()
    env = dict(os.environ, LANG="C.UTF-8", LC_ALL="C.UTF-8", PYTHONIOENCODING="utf-8")
    env.update(PYTHONUTF8="1", FISHROS_UTF8_RESTARTED="1")
    os.execve(sys.executable, [sys.executable] + sys.argv, env)


if __name__ == "__main__":
    ensure_utf8()
    run_exc = []

    try:
        main()
    except Exception as e:
        import traceback

        print(
            "\r\n检测到程序发生异常退出，请打开：https://fishros.org.cn/forum 携带如下内容进行反馈\n\n"
        )
        print("标题：使用一键安装过程中遇到程序崩溃")
        print("```")
        traceback.print_exc()
        run_exc.append(traceback.format_exc())
        print("```")
        print("本次运行详细日志文件已保存至 /tmp/fishros_install.log")

    try:
        with open("/tmp/fishros_install.log", "w", encoding="utf-8") as f:
            for exec in run_exc:
                print(exec, file=f)  # 打印异常输出到文件中
            for text, end in tracing.logs:
                print(text, file=f, end=end)  # 打印输出到文件中
            for text in tracing.err_logs:
                print(text, file=f)  # 打印输出到文件中
        # if tracing.need_report:
        #     print("")
        #     input('检测到本次运行出现失败命令,直接退出按Ctrl+C,按任意键上传日志并退出\n')
        #     ret = os.system("""curl -s -F "file=@/tmp/fishros_install.log" http://103.226.124.73:5000/upload > /tmp/fishros_upload 2>&1""")
        #     if ret == 0:
        #         with open("/tmp/fishros_upload","r") as f:
        #             print("错误日志上传成功，反馈码:",f.read())
        #     else:
        #         print("日志上传失败，若还需反馈请手动发帖!")
    except:
        pass
