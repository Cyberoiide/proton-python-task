from typing import List, Tuple, NamedTuple

# NamedTuple to store host information
class Host(NamedTuple):
    group: str
    addr: str
    port: int
    user: str
    password: str

# parses an inventory file and returns a list of Host objects
def parse_inventory(path: str) -> List[Host]:
    hosts = []
    with open(path, "r") as file:
        current_group = None
        for line in file:
            line = line.strip()
            # skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # check for group definition
            if line.startswith("[") and line.endswith("]"):
                current_group = line[1:-1]
            elif current_group:
                # parse host details
                parts = line.split()
                addr = parts[0]
                # check if the second part is a digit (port), otherwise default to 22
                if len(parts) > 1 and parts[1].isdigit():
                    port = int(parts[1])
                    user = parts[2] if len(parts) > 2 else None
                    password = parts[3] if len(parts) > 3 else None
                else:
                    port = 22
                    user = parts[1] if len(parts) > 1 else None
                    password = parts[2] if len(parts) > 2 else None
                hosts.append(Host(current_group, addr, port, user, password))
    return hosts

# test values on local machine
if __name__ == "__main__":
    hosts = parse_inventory("demo_files/demo_inventory.ini")
    print(hosts)
    # for host in hosts:
    #     print(host)