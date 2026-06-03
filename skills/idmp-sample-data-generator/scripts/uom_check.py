#!/usr/bin/env python3
import json
import requests
import re
import sys
import os
import argparse

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
        # 令牌通常在 'token' 或 'data' 字段中
        return data.get('token') or data.get('data', {}).get('token')
    except Exception as e:
        raise ConnectionError(f"登录 IDMP 失败: {e}")

def get_uom_classes(host, port, token, base_url=None):
    """获取系统中所有的单位分类"""
    if base_url:
        url = f"{base_url.rstrip('/')}/api/v1/uomclasses"
    else:
        url = f"http://{host}:{port}/api/v1/uomclasses"
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_uom_class_details(host, port, token, class_id, base_url=None):
    """获取特定单位分类的详细信息（包含单位列表）"""
    if base_url:
        url = f"{base_url.rstrip('/')}/api/v1/uomclasses/{class_id}"
    else:
        url = f"http://{host}:{port}/api/v1/uomclasses/{class_id}"
        
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def create_uom_class(host, port, token, name, uom_name, base_url=None):
    """创建 UOM Class 及其基础单位"""
    if base_url:
        url = f"{base_url.rstrip('/')}/api/v1/uomclasses"
    else:
        url = f"http://{host}:{port}/api/v1/uomclasses"
        
    headers = {"Authorization": f"Bearer {token}"}
    # 使用 uom_name 同时作为基础单位名称和缩写
    payload = {
        "name": name,
        "description": f"由自动化脚本创建的 {name} 单位类型",
        "canonicalUom": uom_name,
        "canonicalAbbr": uom_name
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def create_uom(host, port, token, class_id, uom_name, ref_uom_id, base_url=None):
    """在分类下创建具体的 UOM"""
    if base_url:
        url = f"{base_url.rstrip('/')}/api/v1/uomclasses/{class_id}/uoms"
    else:
        url = f"http://{host}:{port}/api/v1/uomclasses/{class_id}/uoms"
        
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "name": uom_name,
        "description": f"由自动化脚本创建的 {uom_name} 单位",
        "abbreviation": uom_name,
        "refUomId": ref_uom_id,
        "refFactor": 1.0,
        "refOffset": 0.0
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    parser = argparse.ArgumentParser(description='检查 JSON 配置中的 uomClass 和 uom 在系统中是否存在')
    # 登录信息改为单独传入
    parser.add_argument('--host', help='IDMP 系统 Host')
    parser.add_argument('--port', help='IDMP 系统 端口')
    parser.add_argument('--user', help='登录用户名')
    parser.add_argument('--password', help='登录密码')
    parser.add_argument('--state', help='state.json 文件路径，从中读取登录信息')
    # 配置文件路径
    parser.add_argument('--sample_data', required=True, help='示例数据 JSON 文件路径 (sample_data.json)')
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
        # 1. 登录获取 Token
        conn_str = base_url if base_url else f"{host}:{port}"
        print(f"正在连接到 IDMP ({conn_str})...")
        token = login(host, port, user, password, base_url=base_url)
        if not token:
            print("错误：无法获取登录令牌。")
            return
        print("登录成功，正在加载配置文件...")

        # 2. 读取示例数据文件
        if not os.path.exists(args.sample_data):
            print(f"错误：未找到示例数据文件: {args.sample_data}")
            return
            
        with open(args.sample_data, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
        print("配置文件加载成功。")

        # 3. 从模板中提取 (uomClass, uom) 组合
        required_uoms = set()
        for template in sample_data.get('templates', []):
            for stb in template.get('super_tables', []):
                for metric in stb.get('metrics', []):
                    uom_class_name = metric.get('uomClass')
                    uom_name = metric.get('uom')
                    # 只有当 uom 和 uomClass 同时为空或空格时，才认为无配置并跳过检查
                    if (uom_class_name and uom_class_name.strip()) or (uom_name and uom_name.strip()):
                        required_uoms.add((uom_class_name or "", uom_name or ""))

        if not required_uoms:
            print(f"在 {os.path.basename(args.sample_data)} 中未发现 uomClass/uom 配置。")
            return

        print(f"准备检查 {len(required_uoms)} 组单位配置...")

        # 4. 获取并匹配单位数据
        print("正在获取系统所有的单位分类信息...")
        system_classes_raw = get_uom_classes(host, port, token, base_url=base_url)
        
        # 处理不同可能的 API 返回格式 (data, list, 或直接返回列表)
        if isinstance(system_classes_raw, dict):
            system_classes = system_classes_raw.get('data') or system_classes_raw.get('list') or system_classes_raw
            if isinstance(system_classes, dict) and 'list' in system_classes:
                system_classes = system_classes['list']
        else:
            system_classes = system_classes_raw
            
        if not isinstance(system_classes, list):
            # 尝试处理分页包装
            if isinstance(system_classes, dict) and 'data' in system_classes:
                 system_classes = system_classes['data']

        if not isinstance(system_classes, list):
            print(f"警告：无法解析单位分类列表。")
            system_classes = []

        class_info = {c['name']: {
            'id': c.get('id'),
            'base_unit_abbr': c.get('canonicalAbbr'),
            'base_unit_id': c.get('canonicalId')
        } for c in system_classes if 'name' in c}
        
        # 建立全局单位映射: abbreviation -> list of class names
        print(f"系统中共发现 {len(system_classes)} 个单位分类，正在拉取详细信息以建立全局索引...")
        global_uom_map = {}
        for idx, c in enumerate(system_classes):
            class_id = c.get('id')
            class_name = c.get('name')
            if not class_id: continue
            
            print(f"  [{idx+1}/{len(system_classes)}] 扫描分类: {class_name:<30}", end='\r')
            try:
                details_raw = get_uom_class_details(host, port, token, class_id, base_url=base_url)
                details = details_raw.get('data') or details_raw.get('details') or details_raw
                
                uoms_in_class = []
                if isinstance(details, dict):
                    uoms_in_class = details.get('uomList') or details.get('uoms') or details.get('units') or []
                
                for u in uoms_in_class:
                    abbr = u.get('abbreviation')
                    if abbr:
                        if abbr not in global_uom_map:
                            global_uom_map[abbr] = []
                        if class_name not in global_uom_map[abbr]:
                            global_uom_map[abbr].append(class_name)
            except Exception as e:
                print(f"\n  获取分类 '{class_name}' 失败: {e}")
        
        print(f"\n系统单位信息获取完成。共发现 {len(global_uom_map)} 个独立单位。")

        # 5. 检查要求的组合并执行自动处理逻辑 (第一轮)
        initial_check_results = []
        config_modified = False
        
        for uom_class_name, uom_name in required_uoms:
            class_exists = uom_class_name in class_info
            uom_in_any_classes = global_uom_map.get(uom_name, [])
            status = ""
            
            # --- 增加忽略大小写的匹配检查 ---
            if not uom_in_any_classes:
                uom_lower = uom_name.lower()
                for system_uom in global_uom_map.keys():
                    if system_uom.lower() == uom_lower:
                        print(f"  匹配到大小写不一致的单位: '{uom_name}' -> '{system_uom}'，将自动修正配置...")
                        # 修正 sample_data 中的 uom
                        for template in sample_data.get('templates', []):
                            for stb in template.get('super_tables', []):
                                for metric in stb.get('metrics', []):
                                    if metric.get('uom') == uom_name:
                                        metric['uom'] = system_uom
                                        config_modified = True
                        
                        # 同步更新当前循环变量，以便后续 Case 1 能够直接通过 system_uom 进行 uomClass 的匹配与修正
                        uom_name = system_uom
                        uom_in_any_classes = global_uom_map.get(uom_name, [])
                        break
                        
            # --- 逻辑处理 ---
            
            # 1. 情况 1: 如果 uom 在系统中存在 -> 匹配分类并更新配置
            if uom_in_any_classes:
                system_class_name = uom_in_any_classes[0] # 取第一个匹配的分类
                status = "已匹配系统单位类型"
                
                if system_class_name != uom_class_name:
                    # 替换配置文件中的 uomClass
                    for template in sample_data.get('templates', []):
                        for stb in template.get('super_tables', []):
                            for metric in stb.get('metrics', []):
                                if metric.get('uom') == uom_name:
                                    metric['uomClass'] = system_class_name
                                    config_modified = True
                    # 更新当前变量用于输出
                    uom_class_name = system_class_name
                    class_exists = True
            
            # 2. 情况 2: 如果 uom 和 uomClass 均不存在 -> 自动创建 (需两者均不为空)
            elif not class_exists:
                if uom_class_name.strip() and uom_name.strip():
                    try:
                        print(f"\n正在创建新单位类型 '{uom_class_name}' (基础单位: {uom_name})...")
                        res = create_uom_class(host, port, token, uom_class_name, uom_name, base_url=base_url)
                        # IDMP 创建分类时会自动创建基础单位，所以无需二次创建
                        status = "已添加到系统"
                        # 更新本地缓存以防同一个分类被多次创建
                        data = res.get('data') or res
                        class_info[uom_class_name] = {
                            'id': data.get('id'),
                            'base_unit_abbr': uom_name,
                            'base_unit_id': data.get('canonicalId')
                        }
                        global_uom_map[uom_name] = [uom_class_name]
                        class_exists = True
                    except Exception as e:
                        print(f"创建失败: {e}")
                        status = f"添加失败: {e}"
                else:
                    status = "配置不完整，跳过自动创建"
            
            # 3. 情况 3: 单位不存在但分类存在 -> 标记为待处理
            else:
                status = "待处理"
                
            # 获取最新的分类信息用于输出
            info = class_info.get(uom_class_name, {})
            initial_check_results.append({
                "uom": uom_name,
                "uomExists": "是" if uom_name in global_uom_map else "否",
                "fileClass": uom_class_name,
                "systemClasses": ", ".join([str(x) for x in global_uom_map.get(uom_name, [])]) if uom_name in global_uom_map else "",
                "classId": info.get('id', ""),
                "baseUnit": info.get('base_unit_abbr', ""),
                "baseUnitId": info.get('base_unit_id', ""),
                "status": status
            })

        # 6. --- 第一阶段：保存配置文件 (如果第一轮有修改) ---
        if config_modified:
            with open(args.sample_data, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, ensure_ascii=False, indent=2)
            print(f"\n配置文件 {os.path.basename(args.sample_data)} 已自动更新 uomClass。")

        # 7. --- 第二阶段：输出前的最终校验 (过滤掉已处理的，仅保留真正的待处理条目) ---
        final_pending_results = []
        for res in initial_check_results:
            # 重新确认状态（针对那些在第一轮循环中可能被后续操作间接修复的条目）
            curr_uom = res['uom']
            curr_class = res['fileClass']
            
            # 再次从最新的缓存中校验
            uom_in_sys = global_uom_map.get(curr_uom, [])
            
            # 如果该单位已经在文件要求的分类下存在了，或者已经被自动处理成其他状态，则不再输出
            if uom_in_sys and (curr_class in uom_in_sys):
                continue
            
            if res['status'] == "待处理":
                final_pending_results.append(res)

        # 8. 最终结果输出
        if final_pending_results:
            print("\n发现以下单位配置仍需手动处理:")
            header = f"{'uom':<15} | {'存在?':<5} | {'uomClass':<15} | {'处理情况':<20} | {'uomClass id':<12} | {'基础单位':<8} | {'基础单位id':<12}"
            print("-" * len(header))
            print(header)
            print("-" * len(header))
            
            for res in final_pending_results:
                print(f"{res['uom']:<15} | {res['uomExists']:<5} | {res['fileClass']:<15} | {res['status']:<20} | {str(res['classId']):<12} | {res['baseUnit']:<8} | {str(res['baseUnitId']):<12}")
            
            print("-" * len(header))
            print(f"检测完成，共有 {len(final_pending_results)} 处待手动处理配置（如上表所示）。")
        else:
            print("\n" + "=" * 50)
            print("  检测完成，所有单位配置均已生效或已自动修复，无需手动处理。")
            print("=" * 50)

    except Exception as e:
        print(f"运行出错: {e}")

if __name__ == "__main__":
    main()
