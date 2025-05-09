import paramiko  # type: ignore
from typing import Optional, Tuple

def execute_ssh(host: str, username: str, command: str, password: Optional[str] = None, port: int = 22, timeout: int = 10) -> Tuple[int, str, str]:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port=port, username=username, password=password, timeout=timeout)
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, stdout.read().decode(), stderr.read().decode()
    except Exception as e:
        return -1, "", str(e)
    finally:
        client.close()

if __name__ == "__main__":
    code, out, err = execute_ssh("127.0.0.1", "testuser", "df -h", port=32769, password="password")
    print("Exit code:", code)
    print("Output:", out)
    print("Error:", err)
