# Proton Python Task

## Project Description

This project is a mini-orchestrator inspired by Ansible, written in Python, allowing the execution of bash commands on multiple remote servers via SSH, according to a YAML playbook and a host inventory. It automates the collection of system information or the execution of tasks on groups of servers (web, db, etc.).

## Installation

1. **Clone the repository**

```bash
git clone <repo_url>
cd proton-python-task
```

2. **Create a virtual environment and install dependencies**

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt  # (create if needed: see dependencies below)
```

**Main Dependencies:**
- paramiko
- pyyaml

You can manually install them:
```bash
pip install paramiko pyyaml
```

3. **(Optional) Launch Docker test servers**

To test without real servers, you can launch the test containers:

```bash
docker-compose up --build
```

Don't forget to add a .env file. Could look like this :
```env
USER=testuser
PASSWORD=password
```

## Example Inventory File (`demo_files/demo_inventory.ini`)

```ini
# ip port username password

[webservers]
127.0.0.1 2223 testuser password
127.0.0.1 2224 testuser password

[dbservers]
127.0.0.1 2221 testuser password
127.0.0.1 2222 testuser password
```

## Example Playbook (`demo_files/demo_playbook.yml`)

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
    - name: Memory usage
      bash: free -h || cat /proc/meminfo
    - name: Kernel version
      bash: uname -a
    - name: List running processes
      bash: ps aux --sort=-%mem | head -n 10
    - name: List /var/lib (DB data?)
      bash: ls -lh /var/lib
    - name: Check for MySQL/Postgres
      bash: pgrep mysqld || pgrep postgres || echo "No DB process found"

- hosts: webservers
  tasks:
    - name: Uptime
      bash: uptime
    - name: List root
      bash: ls /
    - name: Disk usage
      bash: df -h
    - name: Memory usage
      bash: free -h || cat /proc/meminfo
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

Run the main script by specifying the playbook and inventory to use (by default, it uses the files in `demo_files/`) :

```bash
python main.py
```

You can also modify the `main.py` file to point to other inventory or playbook files.

## How It Works

- **Inventory**: An INI file listing host groups, their IP addresses, ports, users, and passwords.
- **Playbook**: A YAML file listing, for each group, the tasks to execute (name + bash command).
- **main.py**:
    - Parses the inventory and playbook.
    - For each group, executes the tasks on all hosts in the group in parallel (thread pool).
    - Uses SSH (via Paramiko) to execute commands remotely.
    - Displays the results (stdout, stderr, return code) for each task and each host.

## Structure of Main Files

- `main.py`: Entry point, task execution.
- `parsers/hosts_parsers.py`: Parses the inventory.
- `parsers/yaml_parser.py`: Parses the YAML playbook.
- `execute_ssh.py`: Executes a command via SSH.
- `demo_files/`: Examples of inventory and playbook.
- `docker-compose.yml` + `fakeserver.Dockerfile`: To launch SSH Docker test servers.
- `.env`: To be added manually.

## Example Output

```
=== results for 'dbservers' (2 hosts) ===

--- Host: 127.0.0.1:2221 (user: testuser, group: dbservers) ---
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
- Don't forget the .env file.