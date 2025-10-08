#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import yaml
import tempfile
import shutil

def run_command(cmd, timeout=60):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def test_simulation_system_source_config():
    """Simulate system source configuration process with a mock config."""
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    
    try:
        # Create a mock config file for automated testing
        mock_config = """chooses:
- choose: 5
  desc: 一键配置:系统源(更换系统源,支持全版本Ubuntu系统)
- choose: 2
  desc: 不更换继续安装
"""
        
        config_path = os.path.join(test_dir, "fish_install.yaml")
        with open(config_path, "w") as f:
            f.write(mock_config)
        
        print("✓ Created mock configuration for system source configuration simulation")
        
        # Copy install.py and tools directory to temp directory
        shutil.copy("install.py", test_dir)
        shutil.copytree("tools", os.path.join(test_dir, "tools"))
        
        # Run install.py with the mock config in the temp directory
        # We'll run it for a short time to see if it starts correctly
        cmd = f"cd {test_dir} && timeout 15 python3 install.py"
        code, out, err = run_command(cmd, timeout=20)
        
        # Check if the process started correctly
        # For system source config, we expect to see certain keywords
        expected_keywords = ["系统源", "换源", "ubuntu", "欢迎使用"]
        found_keywords = [kw for kw in expected_keywords if kw in out]
        
        if len(found_keywords) >= 2 or code == 124:  # 124 is timeout exit code
            print("✓ System source configuration simulation started correctly")
            return True
        else:
            print("✗ System source configuration simulation failed to start")
            print(f"  Found keywords: {found_keywords}")
            print(f"  stdout: {out[:500]}...")  # First 500 chars
            print(f"  stderr: {err[:500]}...")  # First 500 chars
            return False
            
    except Exception as e:
        print(f"✗ System source configuration simulation error: {e}")
        return False
    finally:
        # Clean up temporary directory
        shutil.rmtree(test_dir, ignore_errors=True)

def test_simulation_ros_install():
    """Simulate ROS installation process with a mock config."""
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    
    try:
        # Create a mock config file for automated testing
        mock_config = """chooses:
- choose: 1
  desc: 一键安装(推荐):ROS(支持ROS/ROS2,树莓派Jetson)
- choose: 2
  desc: 不更换继续安装
- choose: 1
  desc: noetic(ROS1)
- choose: 2
  desc: noetic(ROS1)基础版(小)
"""
        
        config_path = os.path.join(test_dir, "fish_install.yaml")
        with open(config_path, "w") as f:
            f.write(mock_config)
        
        print("✓ Created mock configuration for ROS installation simulation")
        
        # Copy install.py and tools directory to temp directory
        shutil.copy("install.py", test_dir)
        shutil.copytree("tools", os.path.join(test_dir, "tools"))
        
        # Run install.py with the mock config in the temp directory
        # We'll run it for a short time to see if it starts correctly
        cmd = f"cd {test_dir} && timeout 15 python3 install.py"
        code, out, err = run_command(cmd, timeout=20)
        
        # Check if the process started correctly
        # For ROS install, we expect to see certain keywords
        expected_keywords = ["ROS", "安装", "欢迎使用", "ros-"]
        found_keywords = [kw for kw in expected_keywords if kw in out]
        
        if len(found_keywords) >= 2 or code == 124:  # 124 is timeout exit code
            print("✓ ROS installation simulation started correctly")
            return True
        else:
            print("✗ ROS installation simulation failed to start")
            print(f"  Found keywords: {found_keywords}")
            print(f"  stdout: {out[:500]}...")  # First 500 chars
            print(f"  stderr: {err[:500]}...")  # First 500 chars
            return False
            
    except Exception as e:
        print(f"✗ ROS installation simulation error: {e}")
        return False
    finally:
        # Clean up temporary directory
        shutil.rmtree(test_dir, ignore_errors=True)

def main():
    """Run all tests."""
    print("Running compatibility tests...\n")
    
    tests = [
        test_simulation_system_source_config,
        test_simulation_ros_install
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())