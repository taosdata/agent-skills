#!/usr/bin/env python3
import os
import sys
from datetime import datetime

def prepare_project_dir(scenario_name):
    # 获取当前时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 确保场景名称规范化（简单版本：小写化并将空格/连字符替换为下划线）
    scenario_name_sanitized = scenario_name.strip().lower().replace(" ", "_").replace("-", "_")
    
    # 构建基础目录路径
    base_dir = f"idmp-demo/{scenario_name_sanitized}_{timestamp}"
    final_dir = base_dir
    
    # 检查重置名冲突（虽然时间戳后缀通常能避免冲突）
    if os.path.exists(final_dir):
        counter = 1
        while os.path.exists(f"{base_dir}_{counter}"):
            counter += 1
        final_dir = f"{base_dir}_{counter}"
    
    # 创建完整的目录结构
    os.makedirs(f"{final_dir}/scripts", exist_ok=True)
    os.makedirs(f"{final_dir}/outputs", exist_ok=True)
    
    # 输出最终目录路径，供调用者/Agent 使用
    print(final_dir)
    return final_dir

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 prepare_project_dir.py <场景名称>")
        sys.exit(1)
    
    prepare_project_dir(sys.argv[1])
