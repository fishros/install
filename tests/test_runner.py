#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import subprocess
import os
import sys
import time
import json
import re

# 将项目根目录添加到 Python 路径中，以便能找到 tools 模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def load_test_cases(config_file):
    """加载测试用例"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            test_cases = yaml.safe_load(f)
        return test_cases
    except Exception as e:
        print(f"加载测试配置文件失败: {e}")
        return []

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

def run_install_test(test_case):
    """运行单个安装测试"""
    name = test_case.get('name', 'Unknown Test')
    chooses = test_case.get('chooses', [])
    
    print(f"开始测试: {name}")
    
    # 创建临时配置文件路径
    temp_config = "/tmp/fish_install_test_temp.yaml"
    
    # 确保 /tmp 目录存在
    os.makedirs("/tmp", exist_ok=True)
    
    # 创建临时配置文件
    config_data = {'chooses': chooses}
    try:
        with open(temp_config, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)
        print(f"已创建临时配置文件: {temp_config}")
    except Exception as e:
        print(f"创建临时配置文件失败: {e}")
        return False, ""
    
    # 备份原始的 fish_install.yaml (如果存在)
    original_config = "../fish_install.yaml"
    backup_config = "../fish_install.yaml.backup"
    if os.path.exists(original_config):
        try:
            os.rename(original_config, backup_config)
            print(f"已备份原始配置文件至: {backup_config}")
        except Exception as e:
            print(f"备份原始配置文件失败: {e}")
            # 即使备份失败也继续执行，因为我们会在最后恢复
    
    # 将临时配置文件复制为当前配置文件和/tmp/fishinstall/tools/fish_install.yaml
    try:
        import shutil
        shutil.copy(temp_config, original_config)
        print(f"已将临时配置文件复制为: {original_config}")
        
        # 同时将配置文件复制到/tmp/fishinstall/tools/目录下
        fishinstall_config = "/tmp/fishinstall/tools/fish_install.yaml"
        # 确保目录存在
        os.makedirs(os.path.dirname(fishinstall_config), exist_ok=True)
        shutil.copy(temp_config, fishinstall_config)
        print(f"已将临时配置文件复制为: {fishinstall_config}")
    except Exception as e:
        print(f"复制配置文件失败: {e}")
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
        process = subprocess.Popen(
            [sys.executable, "../install.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 等待进程结束 (设置一个合理的超时时间，例如300秒)
        stdout, _ = process.communicate(timeout=300)
        output = stdout
        
        # 打印输出
        print("=== 脚本输出开始 ===")
        print(stdout)
        print("=== 脚本输出结束 ===")
        
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
        print(f"测试超时: {name} (超过300秒)")
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
    config_file = "fish_install_test.yaml"
    
    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        print(f"错误: 找不到测试配置文件 {config_file}")
        sys.exit(1)
    
    # 加载测试用例
    test_cases = load_test_cases(config_file)
    if not test_cases:
        print("错误: 没有找到有效的测试用例")
        sys.exit(1)
    
    print(f"共找到 {len(test_cases)} 个测试用例")
    
    # 运行所有测试用例并收集结果
    results = []
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- 测试用例 {i+1}/{len(test_cases)} ---")
        success, output = run_install_test(test_case)
        case_name = test_case.get('name', f'Test Case {i+1}')
        
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
        print(f"\n详细测试报告已保存至: {report_file}")
    except Exception as e:
        print(f"保存测试报告失败: {e}")
    
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
