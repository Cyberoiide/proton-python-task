from typing import List, Dict
from parsers.yaml_parser import parse_playbook
from parsers.hosts_parsers import parse_inventory
from scripts.task_runner import TaskRunner
from scripts.models import Host

# coordinates the execution of tasks on hosts
class Coordinator:
    def __init__(self, playbook_file: str, inventory_file: str):
        self.playbook_file = playbook_file
        self.inventory_file = inventory_file

    def run(self) -> None:
        playbook = parse_playbook(self.playbook_file)
        raw_hosts = parse_inventory(self.inventory_file)

        group_hosts: Dict[str, List[Host]] = {}
        for host in raw_hosts:
            group_hosts.setdefault(host.group, []).append(host)

        task_runner = TaskRunner()
        for group, tasks in playbook.items():
            hosts = group_hosts.get(group, [])
            if not hosts:
                print(f"\n[!] no host found for '{group}'\n")
                continue

            print(f"\n=== results for '{group}' ({len(hosts)} hosts) ===\n")
            task_runner.run_tasks(hosts, tasks)
