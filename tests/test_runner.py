#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import subprocess
import os
import sys
import time
import json
import re
import argparse

# 将项目根目录添加到 Python 路径中，以便能找到 tools 模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# 导入 distro 库以获取系统版本代号
try:
    import distro
    HAVE_DISTRO = True
except ImportError:
    HAVE_DISTRO = False

def load_test_cases(config_file):
    """加载测试用例"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            test_cases = yaml.safe_load(f)
        return test_cases
    except Exception as e:
        print("加载测试配置文件失败: {}".format(e))
        return []

def get_ubuntu_codename():
    """获取Ubuntu系统的版本代号"""
    if HAVE_DISTRO:
        # 使用 distro 库获取系统信息
        codename = distro.codename()
        if codename:
            return codename.lower()
    
    # 备用方法：尝试使用 lsb_release 命令
    try:
        result = subprocess.run(['lsb_release', '-cs'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip().lower()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # 备用方法：从 /etc/os-release 文件中读取
    try:
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.startswith('UBUNTU_CODENAME='):
                    codename = line.split('=')[1].strip().strip('"')
                    return codename.lower()
                elif line.startswith('VERSION_CODENAME='):
                    codename = line.split('=')[1].strip().strip('"')
                    return codename.lower()
    except FileNotFoundError:
        pass
    
    # 如果所有方法都失败，返回 None
    return None

def check_output_for_errors(output):
    """检查输出中是否包含错误信息"""
    error_keywords = [
        "ModuleNotFoundError",
        "ImportError",
        "Exception",
        "Error:",
        "Traceback",
        "检测到程序发生异常退出"
    ]
    
    for line in output.split('\n'):
        for keyword in error_keywords:
            if keyword in line:
                return True
    return False

def generate_html_report(report, output_file):
    """生成HTML格式的测试报告"""
    html_content = """
<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>一键安装工具测试报告</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .summary {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .test-case {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .passed {
            border-left: 5px solid #4CAF50;
        }
        .failed {
            border-left: 5px solid #f44336;
        }
        .test-name {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .test-status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            color: white;
        }
        .status-passed {
            background-color: #4CAF50;
        }
        .status-failed {
            background-color: #f44336;
        }
        .output {
            background-color: #000000;
            color: #e0e0e0;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class=\"header\">
        <h1>一键安装工具测试报告</h1>
        <p>生成时间: """ + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + """</p>
    </div>
    
    <div class=\"summary\">
        <h2>测试摘要</h2>
        <p>总计: """ + str(report["summary"]["total"]) + """</p>
        <p>通过: """ + str(report["summary"]["passed"]) + """</p>
        <p>失败: """ + str(report["summary"]["failed"]) + """</p>
    </div>
    
    <div class=\"details\">
        <h2>详细测试结果</h2>
"""

    for test_case in report["details"]:
        status_class = "passed" if test_case["success"] else "failed"
        status_text = "通过" if test_case["success"] else "失败"
        status_style = "status-passed" if test_case["success"] else "status-failed"
        
        html_content += """
        <div class=\"test-case {}\">
            <div class=\"test-name\">
                {}
                <span class=\"test-status {}\">{}<\/span>
            <\/div>
            <div class=\"output-title\">输出日志:<\/div>
            <div class=\"output\">{}<\/div>
        <\/div>
""".format(status_class, test_case["name"], status_style, status_text, test_case["output"])

    html_content += """
    </div>
    
    <div class=\"footer\">
        <p>测试报告由一键安装工具自动生成</p>
    </div>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

def run_install_test(test_case):

    """运行单个安装测试"""
    name = test_case.get('name', 'Unknown Test')
    chooses = test_case.get('chooses', [])
    
    print("开始测试: {}".format(name))
    
    # 创建临时配置文件路径
    temp_config = "/tmp/fish_install_test_temp.yaml"
    
    # 确保 /tmp 目录存在
    os.makedirs("/tmp", exist_ok=True)
    
    # 创建临时配置文件
    config_data = {'chooses': chooses}
    try:
        with open(temp_config, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)
        print("已创建临时配置文件: {}".format(temp_config))
    except Exception as e:
        print("创建临时配置文件失败: {}".format(e))
        return False, ""
    
    # 备份原始的 fish_install.yaml (如果存在)
    original_config = "../fish_install.yaml"
    backup_config = "../fish_install.yaml.backup"
    if os.path.exists(original_config):
        try:
            os.rename(original_config, backup_config)
            print("已备份原始配置文件至: {}".format(backup_config))
        except Exception as e:
            print("备份原始配置文件失败: {}".format(e))
            # 即使备份失败也继续执行，因为我们会在最后恢复
    
    # 将临时配置文件复制为当前配置文件和/tmp/fishinstall/tools/fish_install.yaml
    try:
        import shutil
        shutil.copy(temp_config, original_config)
        print("已将临时配置文件复制为: {}".format(original_config))
        
        # 同时将配置文件复制到/tmp/fishinstall/tools/目录下
        fishinstall_config = "/tmp/fishinstall/tools/fish_install.yaml"
        # 确保目录存在
        os.makedirs(os.path.dirname(fishinstall_config), exist_ok=True)
        shutil.copy(temp_config, fishinstall_config)
        print("已将临时配置文件复制为: {}".format(fishinstall_config))
    except Exception as e:
        print("复制配置文件失败: {}".format(e))
        # 恢复备份的配置文件
        if os.path.exists(backup_config):
            try:
                os.rename(backup_config, original_config)
                print(f"已恢复备份的配置文件: {original_config}")
            except:
                pass
        # 清理临时文件
        if os.path.exists(temp_config):
            os.remove(temp_config)
        return False, ""
    
    # 初始化输出和错误信息
    output = ""
    error = ""
    
    # 运行安装脚本
    try:
        # 使用 -u 参数确保输出不被缓冲，以便实时查看日志
        # 直接运行 install.py，它会自动检测并使用 ../fish_install.yaml
        # 增加超时时间为 2 小时 (7200 秒)
        process = subprocess.Popen(
            [sys.executable, "../install.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env={**os.environ, 'FISH_INSTALL_CONFIG': '../fish_install.yaml'}
        )
        
        # 实时打印输出
        print("=== 脚本输出开始 ===")
        while True:
            output_line = process.stdout.readline()
            if output_line == '' and process.poll() is not None:
                break
            if output_line:
                print(output_line.strip())
                output += output_line
                # 确保实时刷新输出
                sys.stdout.flush()
        print("=== 脚本输出结束 ===")
        
        # 等待进程结束，超时时间为 2 小时
        # stdout, _ = process.communicate(timeout=7200)
        # output = stdout
        
        # # 打印输出
        # print("=== 脚本输出开始 ===")
        # print(stdout)
        # print("=== 脚本输出结束 ===")
        
        # 检查退出码和输出中的错误信息
        if process.returncode == 0 and not check_output_for_errors(output):
            print(f"测试通过: {name}")
            return True, output
        else:
            if process.returncode != 0:
                print(f"测试失败: {name} (退出码: {process.returncode})")
            else:
                print(f"测试失败: {name} (脚本中检测到错误)")
            return False, output
    except subprocess.TimeoutExpired:
        print(f"测试超时: {name} (超过7200秒)")
        # 终止进程
        process.kill()
        stdout, _ = process.communicate()
        output = stdout
        return False, output
    except Exception as e:
        print(f"运行测试时发生异常: {e}")
        error = str(e)
        return False, output + "\n" + error
    finally:
        # 恢复备份的配置文件 (如果存在)
        if os.path.exists(backup_config):
            try:
                os.rename(backup_config, original_config)
                print(f"已恢复备份的配置文件: {original_config}")
            except Exception as e:
                print(f"恢复备份的配置文件失败: {e}")
        # 如果没有备份文件，但创建了原始配置文件，则删除它
        elif os.path.exists(original_config):
            try:
                os.remove(original_config)
                print(f"已删除临时创建的配置文件: {original_config}")
            except Exception as e:
                print(f"删除临时配置文件失败: {e}")
        # 清理临时配置文件
        if os.path.exists(temp_config):
            try:
                os.remove(temp_config)
                print(f"已清理临时配置文件: {temp_config}")
            except Exception as e:
                print(f"清理临时配置文件失败: {e}")

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='运行一键安装工具测试')
    parser.add_argument('--target-os-version', type=str, help='目标Ubuntu版本代号 (例如: bionic, focal, jammy, noble)')
    args = parser.parse_args()
    
    target_os_version = args.target_os_version
    if target_os_version:
        print(f"目标系统版本: {target_os_version}")
    else:
        # 自动检测系统版本代号
        target_os_version = get_ubuntu_codename()
        if target_os_version:
            print(f"自动检测到系统版本: {target_os_version}")
        else:
            print("未指定目标系统版本，也未能自动检测到系统版本")
    
    config_file = "fish_install_test.yaml"
    
    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        print(f"错误: 找不到测试配置文件 {config_file}")
        sys.exit(1)
    
    # 加载测试用例
    all_test_cases = load_test_cases(config_file)
    if not all_test_cases:
        print("错误: 没有找到有效的测试用例")
        sys.exit(1)
    
    # 根据目标系统版本过滤测试用例
    if target_os_version:
        test_cases = [tc for tc in all_test_cases if tc.get('target_os_version') == target_os_version]
        if not test_cases:
            # 如果没有找到特定于该系统的测试用例，则运行所有没有指定target_os_version的测试用例
            test_cases = [tc for tc in all_test_cases if 'target_os_version' not in tc]
            if not test_cases:
                print(f"错误: 没有找到适用于系统版本 {target_os_version} 的测试用例")
                sys.exit(1)
    else:
        # 如果没有指定目标系统版本，则运行所有没有指定target_os_version的测试用例
        test_cases = [tc for tc in all_test_cases if 'target_os_version' not in tc]
        if not test_cases:
            print("错误: 没有找到适用于所有系统的通用测试用例")
            sys.exit(1)
    
    print(f"共找到 {len(test_cases)} 个适用于当前系统版本的测试用例")
    
    # 运行所有测试用例并收集结果
    results = []
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases):
        print("\n--- 测试用例 {}/{} ---".format(i+1, len(test_cases)))
        success, output = run_install_test(test_case)
        case_name = test_case.get('name', 'Test Case {}'.format(i+1))
        
        result = {
            "name": case_name,
            "success": success,
            "output": output
        }
        results.append(result)
        
        if success:
            passed += 1
        else:
            failed += 1
        # 在测试用例之间添加延迟，避免系统资源冲突
        time.sleep(2)
    
    # 生成详细的测试报告
    report = {
        "summary": {
            "total": len(test_cases),
            "passed": passed,
            "failed": failed
        },
        "details": results
    }
    
    # 将报告保存为 JSON 文件
    report_file = "test_report.json"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("\n详细测试报告已保存至: {}".format(report_file))
    except Exception as e:
        print("保存测试报告失败: {}".format(e))
    
    # 生成HTML格式的测试报告
    html_report_file = "test_report.html"
    try:
        generate_html_report(report, html_report_file)
        print("HTML测试报告已保存至: {}".format(html_report_file))
    except Exception as e:
        print("生成HTML测试报告失败: {}".format(e))
    
    # 输出测试结果摘要
    print("\n=== 测试结果摘要 ===")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {len(test_cases)}")
    
    if failed > 0:
        print("部分测试失败，请检查日志和测试报告。")
        sys.exit(1)
    else:
        print("所有测试通过！")
        sys.exit(0)

if __name__ == "__main__":
    main()