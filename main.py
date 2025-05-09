import concurrent.futures
import argparse
import os
from typing import List, Tuple, Dict, NamedTuple, Optional
from parsers.yaml_parser import parse_playbook
from parsers.hosts_parsers import parse_inventory
from execute_ssh import execute_ssh

class Host(NamedTuple):
    group: str
    addr: str
    port: int
    user: str
    password: str

class TaskResult(NamedTuple):
    addr: str
    port: int
    user: str
    task_name: str
    command: str
    code: Optional[int]
    stdout: str
    stderr: str

def run_task_on_host(host: Host, task: dict) -> TaskResult:
    cmd = task.get("bash")
    label = task.get("name", cmd)
    try:
        code, out, err = execute_ssh(
            host=host.addr,
            username=host.user or "root",
            command=cmd,
            password=host.password,
            port=host.port
        )
        return TaskResult(
            addr=host.addr,
            port=host.port,
            user=host.user,
            task_name=label,
            command=cmd,
            code=code,
            stdout=out.strip(),
            stderr=err.strip(),
        )
    except Exception as e:
        return TaskResult(
            addr=host.addr,
            port=host.port,
            user=host.user,
            task_name=label,
            command=cmd,
            code=None,
            stdout="",
            stderr=f"FAILED: {e}",
        )

def print_task_result(result: TaskResult) -> None:
    print(f"  [Task] {result.task_name}")
    print(f"    [Command] {result.command}")
    print(f"    [Exit code] {result.code}")
    print(f"    [stdout]")
    if result.stdout:
        for line in result.stdout.splitlines():
            print(f"      {line}")
    else:
        print("      (vide)")
    print(f"    [stderr]")
    if result.stderr:
        for line in result.stderr.splitlines():
            print(f"      {line}")
    else:
        print("      (vide)")

def main(playbook_file: str, inventory_file: str) -> None:
    playbook = parse_playbook(playbook_file)
    raw_hosts = parse_inventory(inventory_file)

    group_hosts: Dict[str, List[Host]] = {}
    for host in raw_hosts:
        group_hosts.setdefault(host.group, []).append(host)

    for group, tasks in playbook.items():
        hosts = group_hosts.get(group, [])
        if not hosts:
            print(f"\n[!] no host found for '{group}'\n")
            continue

        print(f"\n=== results for '{group}' ({len(hosts)} hosts) ===\n")
        results_by_host = {}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_host_task = {
                executor.submit(run_task_on_host, host, task): (host, task)
                for host in hosts
                for task in tasks
            }
            for future in concurrent.futures.as_completed(future_to_host_task):
                result = future.result()
                host_key = (result.addr, result.port, result.user)
                results_by_host.setdefault(host_key, []).append(result)

        for host_key, results in results_by_host.items():
            addr, port, user = host_key
            print(f"--- Host: {addr}:{port} (user: {user}, group: {group}) ---")
            for res in results:
                print_task_result(res)
            print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mini SSH Orchestrator")
    parser.add_argument(
        "--playbook", type=str, default="demo_files/demo_playbook.yml",
        help="Path to the YAML playbook"
    )
    parser.add_argument(
        "--inventory", type=str, default="demo_files/demo_inventory.ini",
        help="Path to the inventory file"
    )
    args = parser.parse_args()

    main(args.playbook, args.inventory)
