import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tempfile
from parsers.hosts_parsers import parse_inventory, Host

def test_parse_inventory_valid():
    ini_content = """
[web]
192.168.1.10 22 user1 pass1
192.168.1.11 2222 user2 pass2
[db]
192.168.1.20 3306 dbuser dbpass
"""
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        f.write(ini_content)
        f.flush()
        result = parse_inventory(f.name)
    os.unlink(f.name)
    assert len(result) == 3
    assert result[0] == Host('web', '192.168.1.10', 22, 'user1', 'pass1')
    assert result[1] == Host('web', '192.168.1.11', 2222, 'user2', 'pass2')
    assert result[2] == Host('db', '192.168.1.20', 3306, 'dbuser', 'dbpass')

def test_parse_inventory_empty():
    ini_content = """"""
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        f.write(ini_content)
        f.flush()
        result = parse_inventory(f.name)
    os.unlink(f.name)
    assert result == []

def test_parse_inventory_comments_and_blank():
    ini_content = """
# This is a comment
[web]

192.168.1.10 22 user1 pass1

# Another comment
[db]
192.168.1.20 3306 dbuser dbpass
www.example.com 22 user3 pass3
"""
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        f.write(ini_content)
        f.flush()
        result = parse_inventory(f.name)
    os.unlink(f.name)
    assert len(result) == 3
    assert result[0].group == 'web'
    assert result[1].group == 'db'
    assert result[2].group == 'db'

def test_parse_inventory_missing_fields():
    ini_content = """
[web]
192.168.1.10
192.168.1.11 2222
www.example.com
"""
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        f.write(ini_content)
        f.flush()
        result = parse_inventory(f.name)
    os.unlink(f.name)
    assert result[0] == Host('web', '192.168.1.10', 22, None, None)
    assert result[1] == Host('web', '192.168.1.11', 2222, None, None)
    assert result[2] == Host('web', 'www.example.com', 22, None, None) 