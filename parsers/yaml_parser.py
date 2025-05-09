import yaml
from typing import Dict, List, Any

def parse_playbook(file_path: str) -> Dict[str, List[dict]]:
    with open(file_path, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
            playbook = {}
            if data:
                for item in data:
                    group = item.get('hosts')
                    tasks = item.get('tasks', [])
                    if group:
                        playbook[group] = tasks
            return playbook
        except yaml.YAMLError as exc:
            raise ValueError(f"Error parsing YAML file: {exc}")

# test values on local machine
if __name__ == "__main__":
    parsed = parse_playbook("demo_playbook.yml")
    print(parsed)
    # print(parsed["tasks"])