#!/usr/bin/env python3
import json
import requests
import sys
import os
import argparse

import time

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
        return data.get('token') or (data.get('data', {}).get('token') if isinstance(data.get('data'), dict) else None)
    except Exception as e:
        raise ConnectionError(f"登录 IDMP 失败: {e}")

def upload_sample(host, port, token, json_path, base_url=None):
    """上传示例数据核心逻辑"""
    if base_url:
        url = f"{base_url.rstrip('/')}/api/v1/samples/management"
    else:
        url = f"http://{host}:{port}/api/v1/samples/management"
    
    headers = {"Authorization": f"Bearer {token}"}
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"未找到 JSON 文件: {json_path}")
    
    # 在 JSON 同级目录创建临时占位图
    image_path = os.path.join(os.path.dirname(json_path), "placeholder.jpg")
    if not os.path.exists(image_path):
        with open(image_path, 'wb') as f:
            f.write(b"") # 0字节占位符
        print(f"  已创建系统所需的占位图片: {image_path}")

    files = [
        ('jsonFile', (os.path.basename(json_path), open(json_path, 'rb'), 'application/json')),
        ('imageFile', (os.path.basename(image_path), open(image_path, 'rb'), 'image/jpeg'))
    ]

    try:
        print(f"正在上传数据到 IDMP...")
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        res_data = response.json()
        
        # 提取结果数据
        data = res_data.get('data') or res_data
        sample_id = data.get('id')
        sample_name = data.get('name')
        
        if sample_id:
            print(f"\n[OK] 上传成功!")
            print(f"ID: {sample_id}")
            print(f"名称: {sample_name}")
            return sample_id
        else:
            raise ValueError(f"上传成功但未返回 ID: {res_data}")
            
    finally:
        # 关闭所有打开的文件
        for _, file_info in files:
            file_info[1].close()

def load_sample(host, port, token, sample_id, base_url=None):
    """触发加载示例数据"""
    if base_url:
        url = f"{base_url.rstrip('/')}/api/v1/samples/{sample_id}"
    else:
        url = f"http://{host}:{port}/api/v1/samples/{sample_id}"
    
    headers = {"Authorization": f"Bearer {token}"}
    print(f"正在发起示例数据加载请求 (ID: {sample_id})...")
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    print("  加载请求已受理。")

def poll_status(host, port, token, sample_id, base_url=None):
    """轮询加载状态"""
    if base_url:
        url = f"{base_url.rstrip('/')}/api/v1/samples/{sample_id}"
    else:
        url = f"http://{host}:{port}/api/v1/samples/{sample_id}"
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("开始轮询加载进度...")
    while True:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            res_data = response.json()
            data = res_data.get('data') or res_data
            
            status = data.get('status')
            progress = data.get('progress', 0)
            
            print(f"  当前状态: {status} | 进度: {progress}%", flush=True)
            
            # 完成判定标：LOADED 或 进度 > 30% (视为有效开始生成数据)
            if status == "LOADED" or (status == "GENERATING" and progress > 30):
                print(f"\n[SUCCESS] 示例数据已进入加载/生成阶段!", flush=True)
                return True
            
            if status == "FAILED":
                error_msg = data.get('remark', '未知原因')
                raise RuntimeError(f"示例数据加载失败: {error_msg}")
                
            time.sleep(10)
        except Exception as e:
            print(f"  轮询出错 (10s后重试): {e}")
            time.sleep(10)

def delete_sample(host, port, token, sample_id, base_url=None):
    """清理/删除示例数据及其记录"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 卸载示例数据
    if base_url:
        unload_url = f"{base_url.rstrip('/')}/api/v1/samples/{sample_id}"
    else:
        unload_url = f"http://{host}:{port}/api/v1/samples/{sample_id}"
        
    print(f"正在发起卸载请求 (ID: {sample_id})...")
    try:
        requests.delete(unload_url, headers=headers).raise_for_status()
        print("  卸载请求已发送。")
    except Exception as e:
        print(f"  警告: 卸载请求可能已失败(可能未加载): {e}")

    # 2. 删除管理记录
    if base_url:
        mgmt_url = f"{base_url.rstrip('/')}/api/v1/samples/management/{sample_id}"
    else:
        mgmt_url = f"http://{host}:{port}/api/v1/samples/management/{sample_id}"
        
    print(f"正在删除示例记录 (ID: {sample_id})...")
    requests.delete(mgmt_url, headers=headers).raise_for_status()
    print("  记录删除成功。")

    # 3. 验证是否清除成功
    if base_url:
        check_url = f"{base_url.rstrip('/')}/api/v1/samples"
    else:
        check_url = f"http://{host}:{port}/api/v1/samples"
        
    print("正在验证清除结果...")
    for i in range(5):
        try:
            response = requests.get(check_url, headers=headers)
            response.raise_for_status()
            res_data = response.json()
            # 检查列表中是否还存在此 ID
            samples = res_data.get('data', []) if isinstance(res_data.get('data'), list) else res_data
            if not any(str(s.get('id')) == str(sample_id) for s in samples):
                print(f"[OK] ID {sample_id} 已成功从系统中移除。")
                return True
            print(f"  ID 仍存在，等待 3s ({i+1}/5)...")
            time.sleep(3)
        except Exception as e:
            print(f"  验证过程中出错: {e}")
            time.sleep(3)
    
    raise RuntimeError(f"清理超时: ID {sample_id} 仍残留在系统中。")

def main():
    parser = argparse.ArgumentParser(description='自动上传并加载或清理 IDMP 示例数据')
    parser.add_argument('--host', help='IDMP 系统 Host')
    parser.add_argument('--port', help='IDMP 系统 端口')
    parser.add_argument('--user', help='登录用户名')
    parser.add_argument('--password', help='登录密码')
    parser.add_argument('--state', help='state.json 文件路径，从中读取登录信息')
    parser.add_argument('--sample_data', help='示例数据 JSON 文件路径 (上传模式必备)')
    parser.add_argument('--cleanup', help='要清理的示例数据 ID (清理模式)')
    
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
        
        # 2. 执行清理 (如果指定了 --cleanup)
        if args.cleanup:
            delete_sample(host, port, token, sample_id=args.cleanup, base_url=base_url)
            return

        # 3. 执行上传 (目前为单次上传模式)
        if not args.sample_data:
            parser.error("--sample_data 为必填项，除非使用 --cleanup 模式。")
            
        sample_id = upload_sample(host, port, token, args.sample_data, base_url=base_url)
        
        # 4. 触发加载与轮询，失败则自动清理
        try:
            # 触发加载
            load_sample(host, port, token, sample_id, base_url=base_url)
            # 轮询状态
            poll_status(host, port, token, sample_id, base_url=base_url)
        except Exception as e:
            print(f"\n[ERROR] 加载失败，正在自动清理残留资源 (ID: {sample_id})...")
            try:
                delete_sample(host, port, token, sample_id, base_url=base_url)
            except Exception as delete_err:
                print(f"  警告: 清理失败: {delete_err}")
            
            # 抛出原始错误
            raise RuntimeError(f"数据加载与执行异常: {e}")
        
    except Exception as e:
        print(f"\n[FAIL] 运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
