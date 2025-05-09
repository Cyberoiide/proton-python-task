import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest # type: ignore
from unittest import mock
from main import run_task_on_host, TaskResult, Host

@mock.patch('main.execute_ssh')
def test_run_task_on_host_success(mock_ssh):
    mock_ssh.return_value = (0, 'ok', '')
    host = Host('web', '1.2.3.4', 22, 'user', 'pw')
    task = {'name': 'echo', 'bash': 'echo hello'}
    result = run_task_on_host(host, task)
    assert isinstance(result, TaskResult)
    assert result.code == 0
    assert result.stdout == 'ok'
    assert result.stderr == ''
    assert result.task_name == 'echo'
    assert result.command == 'echo hello'

@mock.patch('main.execute_ssh')
def test_run_task_on_host_failure(mock_ssh):
    mock_ssh.side_effect = Exception('ssh failed')
    host = Host('web', '1.2.3.4', 22, 'user', 'pw')
    task = {'name': 'fail', 'bash': 'badcmd'}
    result = run_task_on_host(host, task)
    assert result.code is None
    assert 'FAILED' in result.stderr
    assert result.task_name == 'fail'
    assert result.command == 'badcmd'

@mock.patch('main.print_task_result')
@mock.patch('main.run_task_on_host')
@mock.patch('main.parse_inventory')
@mock.patch('main.parse_playbook')
def test_main_logic(mock_parse_playbook, mock_parse_inventory, mock_run_task, mock_print):
    # Préparer les mocks
    mock_parse_playbook.return_value = {'web': [{'name': 't1', 'bash': 'ls'}]}
    host = Host('web', '1.2.3.4', 22, 'user', 'pw')
    mock_parse_inventory.return_value = [host]
    mock_result = TaskResult(addr='1.2.3.4', port=22, user='user', task_name='t1', command='ls', code=0, stdout='ok', stderr='')
    mock_run_task.return_value = mock_result

    from main import main
    main('fake_playbook.yml', 'fake_inventory.ini')
    mock_parse_playbook.assert_called_once_with('fake_playbook.yml')
    mock_parse_inventory.assert_called_once_with('fake_inventory.ini')
    mock_run_task.assert_called_once_with(host, {'name': 't1', 'bash': 'ls'})
    mock_print.assert_called() 