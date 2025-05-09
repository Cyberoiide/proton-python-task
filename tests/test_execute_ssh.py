import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest # type: ignore
from unittest import mock # type: ignore
from execute_ssh import execute_ssh
import paramiko # type: ignore

@mock.patch('execute_ssh.paramiko.SSHClient')
def test_execute_ssh_success(mock_ssh_client):
    # prepare mock
    mock_client = mock.Mock()
    mock_ssh_client.return_value = mock_client
    mock_stdout = mock.Mock()
    mock_stderr = mock.Mock()
    mock_stdout.read.return_value = b"command ok"
    mock_stderr.read.return_value = b""
    mock_stdout.channel.recv_exit_status.return_value = 0
    mock_client.exec_command.return_value = (None, mock_stdout, mock_stderr)

    exit_code, out, err = execute_ssh('host', 'user', 'ls', password='pw')
    assert exit_code == 0
    assert out == "command ok"
    assert err == ""

@mock.patch('execute_ssh.paramiko.SSHClient')
def test_execute_ssh_exception(mock_ssh_client):
    mock_client = mock.Mock()
    mock_ssh_client.return_value = mock_client
    mock_client.connect.side_effect = Exception("failed to connect")

    exit_code, out, err = execute_ssh('host', 'user', 'ls', password='pw')
    assert exit_code == -1
    assert out == ""
    assert "failed to connect" in err

@mock.patch('execute_ssh.paramiko.SSHClient')
def test_execute_ssh_non_zero_exit_code(mock_ssh_client):
    # prepare mock
    mock_client = mock.Mock()
    mock_ssh_client.return_value = mock_client
    mock_stdout = mock.Mock()
    mock_stderr = mock.Mock()
    mock_stdout.read.return_value = b"command failed"
    mock_stderr.read.return_value = b"error message"
    mock_stdout.channel.recv_exit_status.return_value = 1
    mock_client.exec_command.return_value = (None, mock_stdout, mock_stderr)

    exit_code, out, err = execute_ssh('host', 'user', 'ls', password='pw')
    assert exit_code == 1
    assert out == "command failed"
    assert err == "error message"

@mock.patch('execute_ssh.paramiko.SSHClient')
def test_execute_ssh_timeout(mock_ssh_client):
    mock_client = mock.Mock()
    mock_ssh_client.return_value = mock_client
    mock_client.connect.side_effect = paramiko.SSHException("timeout")

    exit_code, out, err = execute_ssh('host', 'user', 'ls', password='pw', timeout=1)
    assert exit_code == -1
    assert out == ""
    assert "timeout" in err

@mock.patch('execute_ssh.paramiko.SSHClient')
def test_execute_ssh_auth_failure(mock_ssh_client):
    mock_client = mock.Mock()
    mock_ssh_client.return_value = mock_client
    mock_client.connect.side_effect = paramiko.AuthenticationException("auth failed")

    exit_code, out, err = execute_ssh('host', 'user', 'ls', password='wrong_pw')
    assert exit_code == -1
    assert out == ""
    assert "auth failed" in err

@mock.patch('execute_ssh.paramiko.SSHClient')
def test_execute_ssh_no_password(mock_ssh_client):
    mock_client = mock.Mock()
    mock_ssh_client.return_value = mock_client
    mock_stdout = mock.Mock()
    mock_stderr = mock.Mock()
    mock_stdout.read.return_value = b"command ok"
    mock_stderr.read.return_value = b""
    mock_stdout.channel.recv_exit_status.return_value = 0
    mock_client.exec_command.return_value = (None, mock_stdout, mock_stderr)

    exit_code, out, err = execute_ssh('host', 'user', 'ls')
    assert exit_code == 0
    assert out == "command ok"
    assert err == ""
