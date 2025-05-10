from typing import NamedTuple, Optional

# NamedTuple to store host information
class Host(NamedTuple):
    group: str
    addr: str
    port: int
    user: str
    password: str

# NamedTuple to store task result information
class TaskResult(NamedTuple):
    addr: str
    port: int
    user: str
    task_name: str
    command: str
    code: Optional[int]
    stdout: str
    stderr: str
