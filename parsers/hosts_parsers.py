from typing import List, Tuple, NamedTuple

class Host(NamedTuple):
    group: str
    addr: str
    port: int
    user: str
    password: str

def parse_inventory(path: str) -> List[Host]:
    hosts = []
    with open(path, "r") as file:
        current_group = None
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current_group = line[1:-1]
            elif current_group:
                parts = line.split()
                addr = parts[0]
                port = int(parts[1]) if len(parts) > 1 else 22
                user = parts[2] if len(parts) > 2 else None
                password = parts[3] if len(parts) > 3 else None
                hosts.append(Host(current_group, addr, port, user, password))
    return hosts

# test values on local machine
if __name__ == "__main__":
    hosts = parse_inventory("demo_inventory.ini")
    for host in hosts:
        print(host)