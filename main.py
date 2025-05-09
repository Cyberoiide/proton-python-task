import concurrent.futures
from typing import List, Tuple, Dict
from parsers.yaml_parser import parse_playbook
from parsers.hosts_parsers import parse_inventory
from execute_ssh import execute_ssh

HostTuple = Tuple[str, str, int, str, str]  # (group, ip, port, user, password)

def run_task_on_host(ip: str, port: int, user: str, password: str, task: dict):
    cmd = task.get("bash")
    label = task.get("name", cmd)
    try:
        code, out, err = execute_ssh(
            host=ip,
            username=user or "root",
            command=cmd,
            password=password,
            port=port
        )
        return {
            "ip": ip,
            "port": port,
            "user": user,
            "task_name": label,
            "command": cmd,
            "code": code,
            "stdout": out.strip(),
            "stderr": err.strip(),
        }
    except Exception as e:
        return {
            "ip": ip,
            "port": port,
            "user": user,
            "task_name": label,
            "command": cmd,
            "code": None,
            "stdout": "",
            "stderr": f"FAILED: {e}",
        }

def main(playbook_file: str, inventory_file: str):
    playbook = parse_playbook(playbook_file)  # Dict[group_name -> List[task]]
    # ex : {'fakeserver': [{'name': 'Server uptime', 'bash': 'uptime'}, {'name': 'Server disk usage', 'bash': 'du -h'}], 'webservers': [{'name': 'Server uptime', 'bash': 'uptime'}, {'name': 'Server disk usage', 'bash': 'du -h'}]}
    
    raw_hosts = parse_inventory(inventory_file)  # List[Tuple[group, ip, port, user, pwd]]
    # ex : [('fakeserver', '127.0.0.1', 32769, 'testuser', 'password'), ('anotherserver', '127.0.0.1', 32778, 'testuser2', 'password2')]

    # group hosts by group name 
    group_hosts: Dict[str, List[HostTuple]] = {}
    for group, ip, port, user, pwd in raw_hosts:
        group_hosts.setdefault(group, []).append((group, ip, port, user, pwd))

    for group, tasks in playbook.items():
        hosts = group_hosts.get(group, [])
        if not hosts:
            print(f"\n[!] no host found for '{group}'\n")
            continue

        print(f"\n=== results for '{group}' ({len(hosts)} hosts) ===\n")
        results_by_host = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_host_task = {
                executor.submit(run_task_on_host, ip, port, user, pwd, task): (ip, port, user, task)
                for _, ip, port, user, pwd in hosts
                for task in tasks
            }
            for future in concurrent.futures.as_completed(future_to_host_task):
                result = future.result()
                host_key = (result["ip"], result["port"], result["user"])
                results_by_host.setdefault(host_key, []).append(result)

        for (ip, port, user), results in results_by_host.items():
            print(f"--- Host: {ip}:{port} (user: {user}, group: {group}) ---")
            for res in results:
                print(f"  [Task] {res['task_name']}")
                print(f"    [Command] {res['command']}")
                print(f"    [Exit code] {res['code']}")
                print(f"    [stdout]")
                if res['stdout']:
                    for line in res['stdout'].splitlines():
                        print(f"      {line}")
                else:
                    print("      (vide)")
                print(f"    [stderr]")
                if res['stderr']:
                    for line in res['stderr'].splitlines():
                        print(f"      {line}")
                else:
                    print("      (vide)")
            print()

if __name__ == "__main__":
    main("demo_files/demo_playbook.yml", "demo_files/demo_inventory.ini")