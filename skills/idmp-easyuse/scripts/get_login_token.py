import requests
import json
import argparse
import sys
import os


def login(host, username, password, base_url=None):
    if base_url:
        url = f"{base_url.rstrip('/')}/api/v1/users/login"
    else:
        url = f"{host.rstrip('/')}/api/v1/users/login"
    payload = {"login_name": username, "password": password}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        sys.exit(1)
    return response.json()["token"]


def main():
    parser = argparse.ArgumentParser(
        description="Get an IDMP login token"
    )
    parser.add_argument("--host", help="IDMP host")
    parser.add_argument("--username", help="IDMP username")
    parser.add_argument("--password", help="IDMP password")
    parser.add_argument("--state", help="state.json 文件路径，从中读取登录信息")
    args = parser.parse_args()

    host, user, password, base_url = args.host, args.username, args.password, None

    if args.state:
        if not os.path.exists(args.state):
            print(f"错误: 未找到 state 文件: {args.state}")
            sys.exit(1)
        with open(args.state, "r", encoding="utf-8") as f:
            state_data = json.load(f)
            login_info = state_data.get("idmp-login") or state_data.get("login")
            if login_info:
                base_url = login_info.get("url") or login_info.get("idmp_url")
                user = user or login_info.get("user") or login_info.get("idmp_user")
                password = password or login_info.get("pass") or login_info.get("idmp_pass")

                if not base_url and login_info.get("host"):
                    h = login_info.get("host")
                    p = login_info.get("port", 6042)
                    base_url = f"http://{h}:{p}"
            else:
                print("警告: state 文件中未发现 'idmp-login' 或 'login' 信息")

    if not (base_url or host):
        parser.error("必须提供 --host 或 --state (含有效登录信息)")
    if not user or not password:
        parser.error("必须提供 --username 和 --password，或在 --state 中包含它们")

    token = login(host, user, password, base_url=base_url)
    print(token)


if __name__ == "__main__":
    main()
