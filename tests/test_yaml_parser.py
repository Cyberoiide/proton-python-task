import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tempfile
import pytest # type: ignore
from parsers.yaml_parser import parse_playbook

def test_parse_playbook_valid():
    yaml_content = """
- hosts: servers1
  tasks:
    - name: install nginx
      action: apt name=nginx state=present
- hosts: servers2
  tasks:
    - name: install mysql
      action: apt name=mysql-server state=present
"""
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        f.write(yaml_content)
        f.flush()
        result = parse_playbook(f.name)
    os.unlink(f.name)
    assert 'servers1' in result
    assert 'servers2' in result
    assert result['servers1'][0]['name'] == 'install nginx'
    assert result['servers2'][0]['action'] == 'apt name=mysql-server state=present'

def test_parse_playbook_empty():
    yaml_content = """"""
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        f.write(yaml_content)
        f.flush()
        result = parse_playbook(f.name)
    os.unlink(f.name)
    assert result == {}

def test_parse_playbook_malformed():
    yaml_content = """
- hosts: webservers
  tasks
    - name: install nginx
"""
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        f.write(yaml_content)
        f.flush()
        with pytest.raises(ValueError):
            parse_playbook(f.name)
    os.unlink(f.name)

def test_parse_playbook_no_tasks():
    yaml_content = """
- hosts: webservers
"""
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        f.write(yaml_content)
        f.flush()
        result = parse_playbook(f.name)
    os.unlink(f.name)
    assert 'webservers' in result
    assert result['webservers'] == [] 