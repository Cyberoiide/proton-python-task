import argparse
from scripts.task_coordinator import Coordinator

# main function to run the orchestrator
def main(playbook_file: str, inventory_file: str) -> None:
    coordinator = Coordinator(playbook_file, inventory_file)
    coordinator.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mini SSH Orchestrator")
    parser.add_argument(
        "--playbook", type=str, required=True,
        help="Path to the YAML playbook"
    )
    parser.add_argument(
        "--inventory", type=str, default="/etc/playbook/hosts",
        help="Path to the inventory file (default: /etc/playbook/hosts)"
    )
    args = parser.parse_args()

    main(args.playbook, args.inventory)