import concurrent.futures
from typing import List, Tuple, Dict
from parsers.yaml_parser import parse_playbook
from parsers.hosts_parsers import parse_inventory
from execute_ssh import execute_ssh

HostTuple = Tuple[str, str, int, str, str]  # (group, ip, port, user, password)

def run_task_on_host(ip: str, port: int, user: str, password: str, task: dict) -> str:
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
        result = f"[{ip}] {label} (code: {code})\n{out.strip()}"
        if err.strip():
            result += f"\n[stderr] {err.strip()}"
        return result
    except Exception as e:
        return f"[{ip}] {label} FAILED: {e}"

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

        print(f"\n=== trying for '{group}' ({len(hosts)} hosts) ===")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(run_task_on_host, ip, port, user, pwd, task)
                for _, ip, port, user, pwd in hosts
                for task in tasks
            ]
            for future in concurrent.futures.as_completed(futures):
                print(future.result())

if __name__ == "__main__":
    main("demo_playbook.yml", "demo_inventory.ini")