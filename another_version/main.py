import sys
from utils import build_playbook, run_ansible_playbook
import os

def main():
    if len(sys.argv) < 2:
        print("Please provide pseudo playbook yaml file")
        sys.exit(1)

    pre_playbook = sys.argv[1]
    inventory_file = sys.argv[2] if len(sys.argv) > 2 else '/etc/playbook/hosts'

    playbook_file = build_playbook(pre_playbook)
    return_code = run_ansible_playbook(inventory_file, playbook_file)

    if return_code == 0:
        os.remove(playbook_file)
    else:
        sys.exit(return_code)

if __name__ == '__main__':
    main()