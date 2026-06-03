import json
import argparse
import sys
import requests
import urllib3
import os

# 禁用 urllib3 的不安全请求警告（针对 verify=False）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def export_idmp_tree(host, username, password, output_file, root_name=None):
    # 1. 登录获取 Token
    login_url = f"{host.rstrip('/')}/api/v1/users/login"
    login_payload = {"login_name": username, "password": password}
    
    try:
        print(f"Logging in to {login_url}...")
        response = requests.post(login_url, json=login_payload, verify=False, timeout=10)
        response.raise_for_status()
        login_data = response.json()
        token = login_data.get("token")
        if not token:
            print("Login failed: Token not found in response.")
            sys.exit(1)
        print("Login success, token obtained.")
    except Exception as e:
        print(f"Login error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Server response: {e.response.text}")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}"}

    def fetch_elements_list(parent_id=None):
        print(f"Fetching elements for parent_id: {parent_id}")
        elements_url = f"{host.rstrip('/')}/api/v1/elements"
        params = {
            "current": 1,
            "size": 1000
        }
        if parent_id:
            params["parentId"] = parent_id
            
        try:
            response = requests.get(elements_url, params=params, headers=headers, verify=False, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict):
                if "rows" in data:
                    elements = data["rows"]
                elif "data" in data:
                    elements = data["data"]
                else:
                    elements = []
            elif isinstance(data, list):
                elements = data
            else:
                elements = []
                
            return elements
        except Exception as e:
            print(f"Error fetching elements for {parent_id}: {e}")
            return []

    def fetch_element_attributes(element_id):
        print(f"Fetching attributes for element_id: {element_id}")
        attrs_url = f"{host.rstrip('/')}/api/v1/elements/{element_id}/attributes"
        try:
            response = requests.get(attrs_url, headers=headers, verify=False, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict):
                attrs = data.get("rows") or data.get("data") or []
            elif isinstance(data, list):
                attrs = data
            else:
                attrs = []
                
            return [{"id": a.get("id"), "name": a.get("name")} for a in attrs if isinstance(a, dict)]
        except Exception as e:
            print(f"Error fetching attributes for {element_id}: {e}")
            return []

    def build_node(element):
        el_id = element.get("id")
        el_name = element.get("name", "N/A")
        el_template_id = element.get("templateId") or element.get("template_id")
        
        return {
            "id": el_id,
            "name": el_name,
            "template_id": el_template_id,
            "attributes": fetch_element_attributes(el_id),
            "children": build_tree(parent_id=el_id),
        }

    def build_tree(parent_id=None):
        elements = fetch_elements_list(parent_id)
        
        # 如果是顶层查询且指定了 root_name，则进行过滤
        if not parent_id and root_name:
            target_element = next(
                (e for e in elements if e.get("name") == root_name),
                None
            )
            if target_element:
                return [build_node(target_element)]
            else:
                available_names = [e.get("name") for e in elements if e.get("name")]
                print(f"Warning: Root element with name '{root_name}' not found.")
                print(f"Available top-level elements: {available_names}")
                return []
        
        results = []
        for element in elements:
            results.append(build_node(element))
        return results

    # 从根节点开始构建
    tree_data = build_tree(parent_id=None)

    # 导出结果：如果有且只有一个根节点，直接输出该节点；否则输出列表
    output_data = tree_data if len(tree_data) > 1 else (tree_data[0] if tree_data else {})

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Tree structure exported to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export IDMP element tree to JSON using API")
    parser.add_argument("--host", help="IDMP host URL")
    parser.add_argument("--user", help="IDMP username")
    parser.add_argument("--password", help="IDMP password")
    parser.add_argument("--state", help="state.json 文件路径，从中读取登录信息")
    parser.add_argument("--output", default="idmp_tree.json", help="Output file path")
    parser.add_argument("--root-name", help="Only export subtree starting with this name")
    parser.add_argument("--sample-data", help="Path to sample_data.json to extract root name from")
    parser.add_argument("--update", action="store_true", help="Update mode: re-fetch tree using root name from existing output file")

    args = parser.parse_args()

    host, user, password = args.host, args.user, args.password

    # 如果提供了 state.json，则从中读取登录信息
    if args.state:
        if not os.path.exists(args.state):
            print(f"错误: 未找到 state 文件: {args.state}")
            sys.exit(1)
        with open(args.state, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
            login_info = state_data.get('idmp-login') or state_data.get('login')
            if login_info:
                host = host or login_info.get('url') or login_info.get('idmp_url')
                user = user or login_info.get('user') or login_info.get('idmp_user')
                password = password or login_info.get('pass') or login_info.get('idmp_pass')
                
                # 如果没有 host (url)，尝试拼凑
                if not host and login_info.get('host'):
                    h = login_info.get('host')
                    p = login_info.get('port', 6042)
                    host = f"http://{h}:{p}"
            else:
                print(f"警告: state 文件中未发现 'idmp-login' 或 'login' 信息")

    # 校验必要参数
    if not host or not user or not password:
        parser.error("必须提供 --host/--user/--password 或在 --state 中包含有效登录信息")

    root_name = args.root_name

    # 更新模式：如果未指定 root_name，尝试从已存在的输出文件中提取根节点名称
    if args.update and not root_name and os.path.exists(args.output):
        try:
            with open(args.output, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if isinstance(existing_data, dict):
                    root_name = existing_data.get('name')
                elif isinstance(existing_data, list) and len(existing_data) == 1:
                    root_name = existing_data[0].get('name')
            
            if root_name:
                print(f"Update mode: re-fetching tree for root '{root_name}' (detected from {args.output})")
        except Exception as e:
            print(f"Update mode warning: failed to parse existing file {args.output}: {e}")

    if args.sample_data:
        try:
            with open(args.sample_data, 'r', encoding='utf-8') as f:
                data = json.load(f)
                info_name = data.get('info', {}).get('name')
                tree_root_value = data.get('tree_root', {}).get('value')
                
                if not root_name:
                    # 如果用户未提供 root_name (且更新模式也没发现)，则自动从 sample_data 提取
                    root_name = tree_root_value or info_name
                    if root_name:
                        print(f"Auto-extracted root name '{root_name}' from {args.sample_data}")
                elif root_name == info_name and tree_root_value and tree_root_value != info_name:
                    # 特殊逻辑：如果发现 root_name 与项目名一致，但 tree_root.value 存在且不同，可能需要修正
                    # 这种情况通常发生在从旧的 sample_data 提取时，或者更新模式提取到了 info.name 但其实应该用 tree_root.value
                    print(f"Root name '{root_name}' refers to project. Correcting to actual tree root: '{tree_root_value}'")
                    root_name = tree_root_value
        except Exception as e:
            print(f"Error reading sample data file: {e}")

    export_idmp_tree(host, user, password, args.output, root_name)
