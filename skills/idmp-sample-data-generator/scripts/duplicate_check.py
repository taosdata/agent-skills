#!/usr/bin/env python3
import json
import requests
import sys
import os
import argparse
import re

def login(host, port, user, password, base_url=None):
    """登录 IDMP 获取 Token"""
    if base_url:
        url = f"{base_url.rstrip('/')}/api/v1/users/login"
    else:
        url = f"http://{host}:{port}/api/v1/users/login"
    
    payload = {
        "login_name": user,
        "password": password
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get('token') or data.get('data', {}).get('token')
    except Exception as e:
        raise ConnectionError(f"登录 IDMP 失败: {e}")

def get_existing_names(host, port, token, endpoint, base_url=None):
    """从指定 API 获取已存在的名称列表"""
    if base_url:
        url = f"{base_url.rstrip('/')}/api/v1/{endpoint}"
    else:
        url = f"http://{host}:{port}/api/v1/{endpoint}"
        
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        res_data = response.json()
        
        # 处理可能的多种返回格式内容
        items = []
        if isinstance(res_data, list):
            items = res_data
        elif isinstance(res_data, dict):
            items = res_data.get('data') or res_data.get('list') or res_data.get('items') or []
            if isinstance(items, dict) and 'list' in items:
                items = items['list']
        
        if not isinstance(items, list):
            return set()
            
        return {item.get('name') for item in items if item.get('name')}
    except Exception as e:
        print(f"获取 {endpoint} 失败: {e}")
        return set()

def get_unique_name(name, existing_names):
    """如果名称冲突，生成后缀递增的新名称"""
    if name not in existing_names:
        return name
    
    counter = 1
    new_name = f"{name}_{counter}"
    while new_name in existing_names:
        counter += 1
        new_name = f"{name}_{counter}"
    return new_name

def update_tree_references(tree_list, old_name, new_name):
    """递归更新 trees 中引用的 template 名称"""
    for node in tree_list:
        if node.get('template') == old_name:
            node['template'] = new_name
        if 'children' in node and isinstance(node['children'], list):
            update_tree_references(node['children'], old_name, new_name)

def main():
    parser = argparse.ArgumentParser(description='检查示例数据名称和元素模板是否与系统中冲突，并自动修复')
    parser.add_argument('--host', help='IDMP 系统 Host')
    parser.add_argument('--port', help='IDMP 系统 端口')
    parser.add_argument('--user', help='登录用户名')
    parser.add_argument('--password', help='登录密码')
    parser.add_argument('--state', help='state.json 文件路径，从中读取登录信息')
    parser.add_argument('--sample_data', required=True, help='示例数据 JSON 文件路径')
    args = parser.parse_args()

    host, port, user, password, base_url = args.host, args.port, args.user, args.password, None

    # 如果提供了 state.json，则从中读取登录信息
    if args.state:
        if not os.path.exists(args.state):
            print(f"错误: 未找到 state 文件: {args.state}")
            sys.exit(1)
        with open(args.state, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
            login_info = state_data.get('idmp-login') or state_data.get('login')
            if login_info:
                base_url = login_info.get('url') or login_info.get('idmp_url')
                user = user or login_info.get('user') or login_info.get('idmp_user')
                password = password or login_info.get('pass') or login_info.get('idmp_pass')
                # 如果没有 base_url，尝试拼凑
                if not base_url and login_info.get('host'):
                    host = login_info.get('host')
                    port = login_info.get('port', 6042)
            else:
                print(f"警告: state 文件中未发现 'idmp-login' 或 'login' 信息")

    # 校验必要参数
    if not (base_url or (host and port)):
        parser.error("必须提供 (--host 和 --port) 或 --state (含有效登录信息)")
    if not user or not password:
        parser.error("必须提供 --user 和 --password，或在 --state 中包含它们")

    try:
        # 1. 登录
        print("正在登录 IDMP...")
        token = login(host, port, user, password, base_url=base_url)
        
        # 2. 读取 JSON
        with open(args.sample_data, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
        
        modified = False
        
        # 3. 检查示例数据名称 (Sample Name)
        print("正在检查示例数据名称冲突...")
        existing_samples = get_existing_names(host, port, token, "samples/management", base_url=base_url)
        # 同时也检查 samples 路径以防万一
        existing_samples.update(get_existing_names(host, port, token, "samples", base_url=base_url))
        
        current_sample_name = sample_data.get('info', {}).get('name')
        if current_sample_name:
            new_sample_name = get_unique_name(current_sample_name, existing_samples)
            if new_sample_name != current_sample_name:
                print(f"  [冲突] 示例数据名称 '{current_sample_name}' -> '{new_sample_name}'")
                sample_data['info']['name'] = new_sample_name
                modified = True
            else:
                print(f"  [OK] 示例数据名称 '{current_sample_name}' 无冲突")

        # 4. 检查元素模板名称 (Element Template Names)
        print("正在检查元素模板名称冲突...")
        existing_templates = get_existing_names(host, port, token, "templates/elements", base_url=base_url)
        
        for template in sample_data.get('templates', []):
            old_name = template.get('name')
            if not old_name: continue
            
            new_name = get_unique_name(old_name, existing_templates)
            if new_name != old_name:
                print(f"  [冲突] 元素模板名称 '{old_name}' -> '{new_name}'")
                template['name'] = new_name
                
                # 更新 trees 中的引用
                if 'trees' in sample_data:
                     update_tree_references(sample_data['trees'], old_name, new_name)
                
                modified = True
                # 更新 existing_templates 以防 JSON 内部也有重复
                existing_templates.add(new_name)
            else:
                print(f"  [OK] 元素模板名称 '{old_name}' 无冲突")

        # 5. 保存修改
        if modified:
            with open(args.sample_data, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, ensure_ascii=False, indent=2)
            print(f"\n修改已保存至: {args.sample_data}")
        else:
            print("\n未发现名称冲突，无需修改。")

    except Exception as e:
        print(f"运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
