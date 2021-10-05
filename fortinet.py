from paramiko import SSHClient, ssh_exception, client
from pprint import pprint
from re import search

# http://docs.paramiko.org/en/stable/api/client.html
# https://github.com/paramiko/paramiko/blob/master/demos/demo_sftp.py


def send_command(host, username, password,  cmd, known_hosts_file="known_hosts"):
    ssh = SSHClient()
    ssh.load_host_keys(known_hosts_file)
    ssh.set_missing_host_key_policy(client.AutoAddPolicy())
    try:
        ssh.connect(host, username=username, password=password, timeout=1)
    except ssh_exception.BadHostKeyException:
        print("Host key not found")
        exit(1)
    except ssh_exception.AuthenticationException:
        print("Bad password")
        exit(2)
    except (ConnectionError, TimeoutError, WindowsError):
        print(f"Timeout connecting to {host}")
        exit(3)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
    lines = ssh_stdout.readlines()
    ssh.save_host_keys(known_hosts_file)
    ssh.close()
    return lines


def get_forti_info(ssh_host, ssh_username, ssh_password):

    lines = send_command(ssh_host, ssh_username, ssh_password, "get system status")
    result = {"version": "n/a", "license": "n/a", "serial": "n/a"}
    for line in lines:
        ver = search("Version:.*", line)
        if ver:
            result["version"] = ver.group().split(": ")[1]
        lic = search("License Expires:.*", line)
        if lic:
            result["license"] = lic.group().split(": ")[1]
        serial_no = search("Serial-Number:.*", line)
        if serial_no:
            result["serial"] = serial_no.group().split(": ")[1]
    return result


forti_data = get_forti_info("host", "user", "password")
pprint(forti_data)
