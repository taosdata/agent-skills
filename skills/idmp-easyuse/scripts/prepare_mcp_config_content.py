#!/usr/bin/env python3
"""
生成 IDMP MCP 配置内容。

流程：
  1. 通过 POST /api/v1/users/api-keys 创建 API Key，获取返回的 id。
  2. 通过 POST /api/v1/users/api-keys/{id}/copy 获取完整 API Key 值。
  3. 根据各 Agent 输出对应的 MCP 配置内容（JSON / TOML / 命令行）。

用法：
  python3 prepare_mcp_config_content.py --state state.json [--title "my-key"] [--format all|json|toml|cli|sse]
  python3 prepare_mcp_config_content.py --host http://localhost:6042 --token <JWT> [--title "my-key"]
"""

import argparse
import json
import os
import sys

import requests


# ---------------------------------------------------------------------------
# API Key 相关操作
# ---------------------------------------------------------------------------

def find_api_key_by_title(base_url: str, token: str, title: str) -> str | None:
    """查询已有 API Key 列表，返回同名记录的 id；未找到则返回 None。"""
    url = f"{base_url.rstrip('/')}/api/v1/users/api-keys"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        # 查询失败不阻断流程，直接返回 None 走创建分支
        return None
    data = resp.json()
    # 兼容 {"data": [...]} 或直接 [...]
    items = data if isinstance(data, list) else (data.get("data") or [])
    for item in items:
        if item.get("title") == title:
            return str(item["id"])
    return None


def create_api_key(base_url: str, token: str, title: str) -> str:
    """创建 API Key，返回新建记录的 id。"""
    url = f"{base_url.rstrip('/')}/api/v1/users/api-keys"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": title}
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code not in (200, 201):
        print(f"创建 API Key 失败 [{resp.status_code}]: {resp.text}", file=sys.stderr)
        sys.exit(1)
    data = resp.json()
    key_id = data.get("id") or (data.get("data") or {}).get("id")
    if not key_id:
        print(f"创建 API Key 响应中未找到 id，响应内容: {data}", file=sys.stderr)
        sys.exit(1)
    return str(key_id)


def copy_api_key(base_url: str, token: str, key_id: str) -> str:
    """通过 copy 接口获取完整 API Key 值。"""
    url = f"{base_url.rstrip('/')}/api/v1/users/api-keys/{key_id}/copy"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(url, headers=headers)
    if resp.status_code not in (200, 201):
        print(f"获取 API Key 内容失败 [{resp.status_code}]: {resp.text}", file=sys.stderr)
        sys.exit(1)
    data = resp.json()
    # 兼容不同响应结构：直接字符串、{"key": ...}、{"data": {"key": ...}} 等
    if isinstance(data, str):
        return data
    api_key = (
        data.get("key")
        or data.get("api_key")
        or data.get("secret")
        or (data.get("data") or {}).get("key")
        or (data.get("data") or {}).get("api_key")
    )
    if not api_key:
        print(f"copy 接口响应中未找到 API Key 值，响应内容: {data}", file=sys.stderr)
        sys.exit(1)
    return api_key


# ---------------------------------------------------------------------------
# 解析 state 文件
# ---------------------------------------------------------------------------

def load_state(state_path: str) -> dict:
    if not os.path.exists(state_path):
        print(f"错误: 未找到 state 文件: {state_path}", file=sys.stderr)
        sys.exit(1)
    with open(state_path, "r", encoding="utf-8") as f:
        return json.load(f)


def login(base_url: str, username: str, password: str) -> str:
    """通过用户名/密码登录，返回 JWT token。"""
    url = f"{base_url.rstrip('/')}/api/v1/users/login"
    resp = requests.post(url, json={"login_name": username, "password": password})
    if resp.status_code != 200:
        print(f"登录失败 [{resp.status_code}]: {resp.text}", file=sys.stderr)
        sys.exit(1)
    token = resp.json().get("token")
    if not token:
        print(f"登录响应中未找到 token，响应内容: {resp.json()}", file=sys.stderr)
        sys.exit(1)
    return token


def resolve_connection(args) -> tuple[str, str]:
    """返回 (base_url, token_or_api_key)。优先使用 API Key，其次 JWT Token，最后降级登录。"""
    base_url = args.host
    token = args.token
    api_key = getattr(args, 'api_key', None)
    username = args.username
    password = args.password

    if args.state:
        state = load_state(args.state)
        login_info = state.get("idmp-login") or state.get("login") or {}

        if not base_url:
            base_url = login_info.get("url") or login_info.get("idmp_url")
            if not base_url:
                host = login_info.get("host")
                port = login_info.get("port", 6042)
                if host:
                    base_url = f"http://{host}:{port}"

        # 优先读取 API Key
        if not api_key:
            api_key = state.get("api_key") or login_info.get("api_key")

        if not token:
            token = state.get("token") or login_info.get("token")

        if not username:
            username = login_info.get("user") or login_info.get("idmp_user")
        if not password:
            password = login_info.get("pass") or login_info.get("idmp_pass")

    if not base_url:
        print("错误: 必须提供 --host 或 --state（含有效 url/host 信息）", file=sys.stderr)
        sys.exit(1)

    # 优先：直接使用 API Key
    if api_key:
        return base_url.rstrip("/"), api_key

    # 次选：使用已有 JWT Token
    if token:
        return base_url.rstrip("/"), token

    # 降级：用用户名/密码自动登录
    if not username or not password:
        print("错误: 未找到 API Key 或 token，且缺少用户名/密码，无法自动登录。"
              "请提供 --api-key、--token 或在 --state 中包含 user/pass", file=sys.stderr)
        sys.exit(1)
    print(f"[0/2] 正在登录 {base_url} ...", file=sys.stderr)
    token = login(base_url, username, password)
    print(f"      登录成功", file=sys.stderr)

    return base_url.rstrip("/"), token


# ---------------------------------------------------------------------------
# 推导对外访问地址（MCP 配置中使用 HTTPS 6034，HTTP 仅排障）
# ---------------------------------------------------------------------------

def resolve_mcp_host(base_url: str, args) -> str:
    """
    MCP 配置优先使用 HTTPS 6034。
    如果用户指定了 --mcp-host，直接使用；
    否则从 base_url 提取 hostname，拼接 https://hostname:6034。
    """
    if args.mcp_host:
        return args.mcp_host.rstrip("/")

    from urllib.parse import urlparse
    parsed = urlparse(base_url)
    hostname = parsed.hostname or parsed.netloc
    return f"https://{hostname}:6034"


# ---------------------------------------------------------------------------
# 输出各 Agent 的 MCP 配置
# ---------------------------------------------------------------------------

def print_json_config(mcp_base: str, api_key: str):
    """通用 JSON 配置（Copilot CLI mcp-config.json / VS Code settings）。"""
    config = {
        "mcpServers": {
            "tdengine-idmp": {
                "type": "http",
                "url": f"{mcp_base}/api/v1/mcp/stream",
                "headers": {
                    "Authorization": f"Bearer {api_key}"
                }
            }
        }
    }
    print("─" * 60)
    print("【JSON 配置】(~/.copilot/mcp-config.json 或 VS Code mcp.json)")
    print("─" * 60)
    print(json.dumps(config, indent=2, ensure_ascii=False))


def print_toml_config(mcp_base: str, api_key: str):
    """Codex ~/.codex/config.toml 配置。"""
    print("─" * 60)
    print("【TOML 配置】(~/.codex/config.toml)")
    print("─" * 60)
    print(f'[mcp_servers.tdengine-idmp]')
    print(f'url = "{mcp_base}/api/v1/mcp/stream"')
    print(f'bearer_token_env_var = "IDMP_API_KEY"')
    print()
    print(f"# 启动 Codex 前请先执行：")
    print(f'export IDMP_API_KEY="{api_key}"')


def print_cli_config(mcp_base: str, api_key: str):
    """Claude Code 命令行配置。"""
    print("─" * 60)
    print("【Claude Code 命令行】")
    print("─" * 60)
    print(
        f'claude mcp add --transport http tdengine-idmp \\\n'
        f'  {mcp_base}/api/v1/mcp/stream \\\n'
        f'  --header "Authorization: Bearer {api_key}"'
    )


def print_form_config(mcp_base: str, api_key: str):
    """通用表单填写参考（Copilot CLI /mcp add 等）。"""
    print("─" * 60)
    print("【通用表单配置 · Streamable HTTP】(Copilot CLI /mcp add 等交互式表单)")
    print("─" * 60)
    rows = [
        ("Server Name",  "tdengine-idmp"),
        ("Server Type",  "HTTP"),
        ("URL",          f"{mcp_base}/api/v1/mcp/stream"),
        ("HTTP Headers", f'{{"Authorization":"Bearer {api_key}"}}'),
    ]
    col_w = max(len(r[0]) for r in rows) + 2
    for k, v in rows:
        print(f"  {k:<{col_w}}: {v}")


def print_sse_json_config(mcp_base: str, api_key: str):
    """SSE JSON 配置（仅在 Agent 明确要求 SSE 时使用）。"""
    config = {
        "mcpServers": {
            "tdengine-idmp": {
                "type": "sse",
                "url": f"{mcp_base}/api/v1/mcp/sse",
                "headers": {
                    "Authorization": f"Bearer {api_key}"
                }
            }
        }
    }
    print("─" * 60)
    print("【SSE · JSON 配置】(仅 Agent 明确要求 SSE 时使用)")
    print("─" * 60)
    print(json.dumps(config, indent=2, ensure_ascii=False))



# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="创建 IDMP API Key 并输出各 Agent 的 MCP 配置内容"
    )
    parser.add_argument("--host",     help="IDMP 服务地址，如 http://localhost:6042")
    parser.add_argument("--api-key",  dest="api_key",
                        help="IDMP API Key（优先于 token 和用户名/密码）")
    parser.add_argument("--token",    help="已有的登录 JWT token（当无 API Key 时使用）")
    parser.add_argument("--username", help="IDMP 用户名（无 token/API Key 时自动登录用）")
    parser.add_argument("--password", help="IDMP 密码（无 token/API Key 时自动登录用）")
    parser.add_argument("--state",    help="state.json 文件路径，从中读取 url/api_key/token")
    parser.add_argument("--mcp-host", dest="mcp_host",
                        help="MCP 配置中使用的对外地址，默认自动推导为 https://<host>:6034")
    parser.add_argument("--title",    default="copilot-mcp",
                        help="API Key 标题（默认: copilot-mcp）")
    parser.add_argument("--format",   default="all",
                        choices=["all", "json", "toml", "cli", "form", "sse"],
                        help="输出格式（默认: all）；sse 仅输出 SSE 相关配置")
    args = parser.parse_args()

    base_url, token = resolve_connection(args)
    mcp_base = resolve_mcp_host(base_url, args)

    # 步骤 1：查找同名 API Key，有则复用，无则创建
    print(f"[1/2] 查找同名 API Key（标题: {args.title}）...", file=sys.stderr)
    key_id = find_api_key_by_title(base_url, token, args.title)
    if key_id:
        print(f"      已找到同名 API Key，id = {key_id}，直接复用", file=sys.stderr)
    else:
        print(f"      未找到同名 API Key，正在创建...", file=sys.stderr)
        key_id = create_api_key(base_url, token, args.title)
        print(f"      创建成功，id = {key_id}", file=sys.stderr)

    # 步骤 2：获取完整 API Key
    print(f"[2/2] 正在获取 API Key 内容...", file=sys.stderr)
    api_key = copy_api_key(base_url, token, key_id)
    print(f"      完成", file=sys.stderr)

    print()
    print(f"MCP Server 地址: {mcp_base}/api/v1/mcp/stream")
    print(f"API Key        : {api_key}")
    print()

    fmt = args.format
    if fmt in ("all", "form"):
        print_form_config(mcp_base, api_key)
        print()
    if fmt in ("all", "json"):
        print_json_config(mcp_base, api_key)
        print()
    if fmt in ("all", "toml"):
        print_toml_config(mcp_base, api_key)
        print()
    if fmt in ("all", "cli"):
        print_cli_config(mcp_base, api_key)
        print()
    if fmt in ("all", "sse"):
        print_sse_json_config(mcp_base, api_key)
        print()


if __name__ == "__main__":
    main()
