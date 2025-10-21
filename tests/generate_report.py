#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import os

def generate_html_report(report, output_file):
    """生成HTML格式的测试报告"""
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            background-color: #f8f8f8;
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
    <div class="header">
        <h1>一键安装工具测试报告</h1>
        <p>生成时间: """ + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + """</p>
    </div>
    
    <div class="summary">
        <h2>测试摘要</h2>
        <p>总计: """ + str(report["summary"]["total"]) + """</p>
        <p>通过: """ + str(report["summary"]["passed"]) + """</p>
        <p>失败: """ + str(report["summary"]["failed"]) + """</p>
    </div>
    
    <div class="details">
        <h2>详细测试结果</h2>
"""

    for test_case in report["details"]:
        status_class = "passed" if test_case["success"] else "failed"
        status_text = "通过" if test_case["success"] else "失败"
        status_style = "status-passed" if test_case["success"] else "status-failed"
        
        html_content += """
        <div class="test-case {}">
            <div class="test-name">
                {}
                <span class="test-status {}">{}</span>
            </div>
            <div class="output-title">输出日志:</div>
            <div class="output">{}</div>
        </div>
""".format(status_class, test_case["name"], status_style, status_text, test_case["output"])

    html_content += """
    </div>
    
    <div class="footer">
        <p>测试报告由一键安装工具自动生成</p>
    </div>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


if __name__ == "__main__":
    # 读取JSON测试报告
    report_file = "test_report.json"
    if os.path.exists(report_file):
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # 生成HTML报告
        html_report_file = "test_report.html"
        generate_html_report(report, html_report_file)
        print("HTML测试报告已生成: {}".format(html_report_file))
    else:
        print("找不到测试报告文件: {}".format(report_file))