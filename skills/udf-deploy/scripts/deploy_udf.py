#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import urllib.request
import urllib.error
import base64
import json
import re

# Colors for pretty logging
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_info(msg):
    print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} {msg}")

def log_success(msg):
    print(f"{Colors.OKGREEN}[SUCCESS] {msg}{Colors.ENDC}")

def log_warning(msg):
    print(f"{Colors.WARNING}[WARNING] {msg}{Colors.ENDC}")

def log_error(msg):
    print(f"{Colors.FAIL}[ERROR] {msg}{Colors.ENDC}", file=sys.stderr)

def run_command(cmd, shell=False, check=True):
    try:
        result = subprocess.run(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.\nStdout: {e.stdout}\nStderr: {e.stderr}")

def detect_docker_containers():
    """Detect running TDengine docker containers."""
    try:
        stdout, _ = run_command(["docker", "ps", "--format", "{{.Names}}"])
        containers = stdout.splitlines()
        td_containers = [c for c in containers if "tsdb" in c or "taos" in c]
        return td_containers
    except Exception:
        return []

def execute_sql_rest(host, port, user, password, sql):
    """Execute SQL using TDengine REST API."""
    url = f"http://{host}:{port}/rest/sql"
    req = urllib.request.Request(url, data=sql.encode('utf-8'))
    
    # Base64 Auth
    auth_str = f"{user}:{password}"
    auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    req.add_header("Authorization", f"Basic {auth_b64}")
    req.add_header("Content-Type", "text/plain")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            resp_body = response.read().decode('utf-8')
            return json.loads(resp_body)
    except urllib.error.URLError as e:
        raise RuntimeError(f"REST API call failed: {e}")

def execute_sql_cli(container_name, user, password, sql):
    """Execute SQL using taos CLI inside Docker container."""
    cmd = ["docker", "exec", "-i", container_name, "taos", "-u", user, "-p", password, "-s", sql]
    stdout, stderr = run_command(cmd)
    if "Query OK" in stdout or "affected" in stdout or not stderr:
        return {"code": 0, "desc": stdout}
    else:
        raise RuntimeError(f"taos CLI execution failed: {stderr or stdout}")

def main():
    parser = argparse.ArgumentParser(description="TDengine UDF Auto Compiler and Deployer")
    parser.add_argument("--src", required=True, help="Path to UDF source file (.c, .cpp, .py)")
    parser.add_argument("--name", help="Registered UDF name (default: filename without extension)")
    parser.add_argument("--type", choices=["scalar", "aggregate"], default="scalar", help="UDF type: scalar or aggregate")
    parser.add_argument("--output-type", required=True, help="Return data type of the UDF (e.g. INT, VARCHAR(100), DOUBLE)")
    parser.add_argument("--bufsize", type=int, help="Buffer size for aggregate UDF (optional)")
    parser.add_argument("--mode", choices=["local", "docker", "remote_ssh"], help="Deployment mode (default: auto-detect)")
    
    # TDengine Connection Settings
    parser.add_argument("--host", default="localhost", help="TDengine host (default: localhost)")
    parser.add_argument("--port", type=int, default=6041, help="TDengine REST API port (default: 6041)")
    parser.add_argument("--user", default="root", help="TDengine username (default: root)")
    parser.add_argument("--password", default="taosdata", help="TDengine password (default: taosdata)")
    
    # Docker Specific Settings
    parser.add_argument("--container", help="Target TDengine Docker container name")
    
    # SSH Specific Settings
    parser.add_argument("--ssh-host", help="SSH host for remote deployment")
    parser.add_argument("--ssh-user", default="root", help="SSH user")
    parser.add_argument("--ssh-port", type=int, default=22, help="SSH port")
    
    args = parser.parse_args()
    
    # Basic path validation
    if not os.path.exists(args.src):
        log_error(f"Source file not found: {args.src}")
        sys.exit(1)
        
    src_filename = os.path.basename(args.src)
    src_name, ext = os.path.splitext(src_filename)
    ext = ext.lower()
    
    if ext not in [".c", ".cpp", ".py"]:
        log_error("Unsupported file extension. Only .c, .cpp, and .py are supported.")
        sys.exit(1)
        
    udf_name = args.name if args.name else src_name
    
    # Mode auto-detection
    mode = args.mode
    container_name = args.container
    
    if not mode:
        # Detect Docker first
        containers = detect_docker_containers()
        if containers:
            mode = "docker"
            container_name = containers[0]
            log_info(f"Auto-detected running TDengine docker container: {container_name}")
        elif args.ssh_host:
            mode = "remote_ssh"
        else:
            mode = "local"
            
    log_info(f"Using deployment mode: {mode}")
    
    # 1. Compilation & Deployment
    target_path = f"/var/lib/taos/udf/{udf_name}{'.so' if ext in ['.c', '.cpp'] else '.py'}"
    
    if mode == "docker":
        if not container_name:
            log_error("Docker container name must be specified or auto-detected in docker mode.")
            sys.exit(1)
            
        # Ensure UDF directory exists inside container
        try:
            run_command(["docker", "exec", container_name, "mkdir", "-p", "/var/lib/taos/udf"])
        except Exception as e:
            log_warning(f"Could not create UDF directory inside container: {e}")
            
        if ext in [".c", ".cpp"]:
            log_info(f"Compiling C/C++ UDF inside Docker container '{container_name}'...")
            # Check if gcc is available in container
            try:
                run_command(["docker", "exec", container_name, "which", "gcc"])
            except Exception:
                log_warning("gcc is not found inside the container. Attempting to install gcc (apt-get)...")
                try:
                    run_command(["docker", "exec", container_name, "apt-get", "update"])
                    run_command(["docker", "exec", container_name, "apt-get", "install", "-y", "gcc", "g++", "make"])
                except Exception as install_err:
                    log_error(f"Failed to install gcc inside container: {install_err}")
                    log_error("Please install gcc inside the container or compile the .so manually.")
                    sys.exit(1)
            
            # Copy source file to container /tmp/
            tmp_src = f"/tmp/{src_filename}"
            log_info(f"Copying source file to container: {tmp_src}")
            run_command(["docker", "cp", args.src, f"{container_name}:{tmp_src}"])
            
            # Compile inside container
            compiler = "g++" if ext == ".cpp" else "gcc"
            compile_cmd = [
                "docker", "exec", container_name,
                compiler, "-shared", "-fPIC", "-O2",
                "-o", target_path,
                tmp_src
            ]
            try:
                run_command(compile_cmd)
                log_success(f"Compilation succeeded inside container. Output: {target_path}")
            except Exception as e:
                log_error(f"Compilation failed inside container: {e}")
                sys.exit(1)
        else: # .py file
            log_info(f"Deploying Python UDF to container '{container_name}'...")
            try:
                run_command(["docker", "cp", args.src, f"{container_name}:{target_path}"])
                log_success(f"Copied Python script to container: {target_path}")
            except Exception as e:
                log_error(f"Failed to copy Python UDF to container: {e}")
                sys.exit(1)
                
    elif mode == "local":
        # Local compile / deploy
        os.makedirs("/var/lib/taos/udf", exist_ok=True)
        if ext in [".c", ".cpp"]:
            log_info("Compiling C/C++ UDF locally...")
            compiler = "g++" if ext == ".cpp" else "gcc"
            compile_cmd = [compiler, "-shared", "-fPIC", "-O2", "-o", target_path, args.src]
            try:
                run_command(compile_cmd)
                log_success(f"Compilation succeeded locally. Output: {target_path}")
            except Exception as e:
                log_error(f"Compilation failed: {e}")
                sys.exit(1)
        else: # .py file
            log_info("Deploying Python UDF locally...")
            import shutil
            try:
                shutil.copy2(args.src, target_path)
                log_success(f"Copied Python script to: {target_path}")
            except Exception as e:
                log_error(f"Failed to copy Python script: {e}")
                sys.exit(1)
                
    elif mode == "remote_ssh":
        if not args.ssh_host:
            log_error("SSH host must be provided for remote_ssh mode.")
            sys.exit(1)
        
        # We need ssh/scp
        ssh_dest = f"{args.ssh_user}@{args.ssh_host}"
        port_arg = ["-P", str(args.ssh_port)]
        ssh_port_arg = ["-p", str(args.ssh_port)]
        
        log_info(f"Copying source file to remote server {args.ssh_host}...")
        try:
            run_command(["scp"] + port_arg + [args.src, f"{ssh_dest}:/tmp/{src_filename}"])
        except Exception as e:
            log_error(f"Failed to scp file to remote: {e}")
            sys.exit(1)
            
        if ext in [".c", ".cpp"]:
            log_info("Compiling UDF on remote server...")
            compiler = "g++" if ext == ".cpp" else "gcc"
            remote_cmd = f"mkdir -p /var/lib/taos/udf && {compiler} -shared -fPIC -O2 -o {target_path} /tmp/{src_filename}"
            try:
                run_command(["ssh"] + ssh_port_arg + [ssh_dest, remote_cmd])
                log_success(f"Compilation succeeded on remote server. Output: {target_path}")
            except Exception as e:
                log_error(f"Remote compilation failed: {e}")
                sys.exit(1)
        else:
            log_info("Deploying Python UDF on remote server...")
            remote_cmd = f"mkdir -p /var/lib/taos/udf && cp /tmp/{src_filename} {target_path}"
            try:
                run_command(["ssh"] + ssh_port_arg + [ssh_dest, remote_cmd])
                log_success(f"Copied script to remote UDF path: {target_path}")
            except Exception as e:
                log_error(f"Failed to deploy on remote server: {e}")
                sys.exit(1)

    # 2. Register Function in TDengine
    log_info("Registering UDF in TDengine...")
    drop_sql = f"DROP FUNCTION IF EXISTS {udf_name};"
    
    # Build CREATE FUNCTION SQL
    func_keyword = "AGGREGATE FUNCTION" if args.type == "aggregate" else "FUNCTION"
    create_sql = f"CREATE {func_keyword} {udf_name} AS '{target_path}' OUTPUTTYPE {args.output_type}"
    if args.type == "aggregate" and args.bufsize:
        create_sql += f" BUFSIZE {args.bufsize}"
    create_sql += ";"
    
    registered = False
    
    # Try REST API first
    try:
        log_info(f"Trying to register UDF via REST API (http://{args.host}:{args.port})...")
        # Execute DROP
        execute_sql_rest(args.host, args.port, args.user, args.password, drop_sql)
        # Execute CREATE
        res = execute_sql_rest(args.host, args.port, args.user, args.password, create_sql)
        if res.get("code") == 0:
            log_success(f"Successfully registered UDF '{udf_name}' via REST API.")
            registered = True
        else:
            log_warning(f"REST API returned error code {res.get('code')}: {res.get('desc')}")
    except Exception as e:
        log_warning(f"Failed to register via REST API: {e}")
        
    # If REST fails and we are in docker, try taos CLI inside container
    if not registered and mode == "docker":
        try:
            log_info(f"Attempting fallback to taos CLI in container '{container_name}'...")
            execute_sql_cli(container_name, args.user, args.password, drop_sql)
            res = execute_sql_cli(container_name, args.user, args.password, create_sql)
            log_success(f"Successfully registered UDF '{udf_name}' via taos CLI.")
            registered = True
        except Exception as e:
            log_error(f"Failed to register via taos CLI: {e}")
            
    # If REST fails and we are local, try local taos CLI
    if not registered and mode == "local":
        try:
            log_info("Attempting fallback to local taos CLI...")
            run_command(["taos", "-u", args.user, "-p", args.password, "-s", drop_sql])
            run_command(["taos", "-u", args.user, "-p", args.password, "-s", create_sql])
            log_success(f"Successfully registered UDF '{udf_name}' via local taos CLI.")
            registered = True
        except Exception as e:
            log_error(f"Failed to register via local taos CLI: {e}")
            
    if not registered:
        log_error("Could not register UDF in TDengine. Please check connectivity and credentials.")
        sys.exit(1)
        
    # 3. Verification Instructions
    print("\n" + "=" * 50)
    log_success(f"UDF {udf_name} has been successfully deployed and registered!")
    print(f"Path: {target_path}")
    print(f"SQL:  {create_sql}")
    print("=" * 50)
    print(f"\nTo verify, you can connect to your TDengine instance and run:")
    print(f"  {Colors.BOLD}SELECT {udf_name}(<column_name>) FROM <table_name> LIMIT 5;{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
