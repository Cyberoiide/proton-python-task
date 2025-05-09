from typing import List, Tuple

def parse_inventory(path: str) -> List[Tuple[str, str, int, str, str]]:
    hosts = []
    with open(path, "r") as f:
        current_group = None
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current_group = line[1:-1]
            elif current_group:
                parts = line.split()
                ip = parts[0]
                port = int(parts[1]) if len(parts) > 1 else 22
                user = parts[2] if len(parts) > 2 else None
                pwd = parts[3] if len(parts) > 3 else None
                hosts.append((current_group, ip, port, user, pwd))
    return hosts

if __name__ == "__main__":
    hosts = parse_inventory("demo_inventory.ini")
    print(hosts)