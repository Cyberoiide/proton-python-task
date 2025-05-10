# SOLUTION

We use Ansible framework to not to reinvent the wheel: https://docs.ansible.com/

# HOW TO USE

## Install deps
```
pip install -r requirements.txt
```
## Smoke test
```
python main.py input.yaml etc/playbook/demo_hosts
```
## Real test:
Please note that ssh credentials need to be pre-configured
```
python main.py input.yaml
```