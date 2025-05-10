import concurrent.futures
from typing import List, Dict
from scripts.execute_ssh import execute_ssh
from scripts.models import Host, TaskResult

# runs tasks on hosts concurrently
class TaskRunner:
    def run_task_on_host(self, host: Host, task: dict) -> TaskResult:
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

    def print_task_result(self, result: TaskResult) -> None:
        print(f"  [Task] {result.task_name}")
        print(f"    [Command] {result.command}")
        print(f"    [Exit code] {result.code}")
        print(f"    [stdout]")
        if result.stdout:
            for line in result.stdout.splitlines():
                print(f"      {line}")
        else:
            print("      (empty)")
        print(f"    [stderr]")
        if result.stderr:
            for line in result.stderr.splitlines():
                print(f"      {line}")
        else:
            print("      (empty)")

    def run_tasks(self, hosts: List[Host], tasks: List[dict]) -> None:
        results_by_host = {}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_host_task = {
                executor.submit(self.run_task_on_host, host, task): (host, task)
                for host in hosts
                for task in tasks
            }
            for future in concurrent.futures.as_completed(future_to_host_task):
                result = future.result()
                host_key = (result.addr, result.port, result.user)
                results_by_host.setdefault(host_key, []).append(result)

        for idx, (host_key, results) in enumerate(results_by_host.items()):
            addr, port, user = host_key
            if idx > 0:
                print("-" * 60)
            print(f"Host: {addr}:{port} (user: {user})")
            for res in results:
                self.print_task_result(res)
            print()
