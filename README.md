# Proton Python Task

## Project Description

This project is a mini-orchestrator inspired by Ansible, written in Python, allowing the execution of bash commands on multiple remote servers via SSH, according to a YAML playbook and a host inventory. It automates the collection of system information or the execution of tasks on groups of servers (web, db, etc.).

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/Cyberoiide/proton-python-task.git
cd proton-python-task
```

2. **Create a virtual environment and install dependencies**

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

3. **(Optional) Launch Docker test servers**

To test without real servers, you can launch the test containers:

```bash
docker-compose -f docker/dev.docker-compose.yml up --build
```

For running only the SSH servers without the orchestrator:

```bash
docker-compose -f docker/only_servers.docker-compose.yml up --build
```

For a production deployment:

```bash
docker-compose -f docker/prod.docker-compose.yml up --build
```

Don't forget to add a .env file. Could look like this:
```env
USER=testuser
PASSWORD=password
```

## Example Inventory File Format

The inventory file is an INI file that defines groups of servers and their connection information:

```ini
# Format: ip port username password

[webservers]
127.0.0.1 2223 testuser password
127.0.0.1 2224 testuser password

[dbservers]
127.0.0.1 2221 testuser password
127.0.0.1 2222 testuser password
```

You can omit the port (defaults to 22), username, and password if needed:

```ini
[webservers]
example.com           # Uses default port 22, no user/pass
example.org 8022      # Custom port, no user/pass
example.net 22 myuser # With username, no password
```

## Example Playbook Format

Playbooks are YAML files that define tasks to run on specific host groups:

```yaml
---
- hosts: dbservers
  tasks:
    - name: Uptime
      bash: uptime
    - name: Hostname
      bash: hostname
    - name: Disk usage
      bash: df -h
    - name: Kernel version
      bash: uname -a
    - name: List /var/lib (DB data?)
      bash: ls -lh /var/lib
    - name: Check for MySQL/Postgres
      bash: pgrep mysqld || pgrep postgres || echo "No DB process found"

- hosts: webservers
  tasks:
    - name: Uptime
      bash: uptime
    - name: Disk usage
      bash: df -h
    - name: Network interfaces
      bash: ip a || ifconfig
    - name: Open ports
      bash: netstat -tuln || ss -tuln
    - name: List /var/www (web root?)
      bash: ls -lh /var/www || echo "/var/www not found"
    - name: Check for nginx/apache
      bash: pgrep nginx || pgrep apache2 || echo "No web server process found"
```

## How to Run the Project

Run the main script by specifying a YAML playbook and optionally an inventory file.

```bash
python main.py --playbook demo_files/demo_playbook.yml --inventory demo_files/demo_inventory.ini
```

- `--playbook`: **Required** – path to your playbook (YAML).
- `--inventory`: *(Optional)* – path to your inventory (INI). Defaults to `/etc/playbook/hosts`.

## How It Works

- **Inventory**: An INI file listing host groups, their IP addresses, ports, users, and passwords.
- **Playbook**: A YAML file listing, for each group, the tasks to execute (name + bash command).
- **main.py**:
    - Parses the inventory and playbook.
    - For each group, executes the tasks on all hosts in the group in parallel (thread pool).
    - Uses SSH (via Paramiko) to execute commands remotely.
    - Displays the results (stdout, stderr, return code) for each task and each host.

## Main Files

- `main.py`: Entry point, task execution.
- `parsers/hosts_parsers.py`: Parses the inventory.
- `parsers/yaml_parser.py`: Parses the YAML playbook.
- `execute_ssh.py`: Executes a command via SSH.
- `demo_files/`: Examples of inventory and playbook.
- `docker/*`: Docker configuration for testing and deployment.

## Testing

The project includes unit tests for all major components. To run the tests:

```bash
pytest
```

The tests cover:
- SSH command execution
- Inventory parsing
- Playbook parsing
- Main orchestration logic

## Docker Deployment Options

### Development Environment
Launches both the SSH test servers and the orchestrator:

```bash
docker-compose -f docker/dev.docker-compose.yml up --build
```

### SSH Servers Only
Launches only the SSH test servers without the orchestrator:

```bash
docker-compose -f docker/only_servers.docker-compose.yml up --build
```

### Production Environment
For deploying the orchestrator in a production environment:

```bash
docker-compose -f docker/prod.docker-compose.yml up --build
```

## Example Output

```
=== results for 'dbservers' (2 hosts) ===

Host: 127.0.0.1:2221 (user: testuser, group: dbservers)
  [Task] Uptime
    [Command] uptime
    [Exit code] 0
    [stdout]
      10:00:00 up 1 day,  2:34,  1 user,  load average: 0.00, 0.01, 0.05
    [stderr]
      (empty)
  ...

--------------------------------------------------------
Host: 127.0.0.1:2222 (user: testuser, group: dbservers)
  [Task] Uptime
    [Command] uptime
    [Exit code] 0
    [stdout]
      10:00:00 up 1 day,  2:34,  1 user,  load average: 0.00, 0.01, 0.05
    [stderr]
      (empty)
  ...
```

## Remarks

- To test with Docker servers, ensure that the ports (2221-2224) are not in use.
- You can adapt the inventory and playbook files to your needs.
- Make sure to create a `.env` file with your credentials.
- The project uses concurrent execution to run tasks in parallel across all hosts for better performance.
- For security, avoid storing plain text passwords in production inventories. Consider using SSH keys.