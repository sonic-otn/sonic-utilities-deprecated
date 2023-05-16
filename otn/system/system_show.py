import click
from tabulate import tabulate
from otn.utils.utils import *

@click.command()
def systime():
    cmd = 'date'
    run_system_command(cmd)

@click.group()
def netstat():
    pass

@netstat.command()
def all():
    cmd = 'netstat -a'
    run_system_command(cmd)

@click.command()
def process():
    cmd = 'ps -ef'
    run_system_command(cmd)

@click.command()
def route():
    cmd = 'route -n'
    run_system_command(cmd)

@click.group()
def system():
    pass

@system.command()
def state():
    cmd = 'service --status-all'
    run_system_command(cmd)

@system.command()
def sshd_alive_timeout():
    cmd = "perl -n -e 'print $1 if /^ClientAliveInterval (\d+)$/' /etc/ssh/sshd_config"
    run_system_command(cmd)

@click.group()
def tcp():
    pass

@tcp.command()
def session():
    cmd = 'netstat -na'
    run_system_command(cmd)

@click.command()
def top():
    cmd = "top -n 1"
    run_system_command(cmd)

@click.command()
def ifconfig():
    cmd = "ifconfig -a"
    run_system_command(cmd)

@click.command()
def users():
    users = run_command("cat /etc/passwd | grep clish_start | cut -d':' -f1", return_cmd=True)
    admin_users = run_command("cat /etc/group | grep sudo | cut -d':' -f4", return_cmd=True)
    data = {'Name': [], 'Role': []}
    for usr in users.splitlines():
        data['Name'].append(usr)
        role = 'monitor'
        if usr in admin_users:
            role = 'administrator'
        data['Role'].append(role)
    print(tabulate(data, headers='keys'))

@click.command('log-file')
def log_file():
    cmd = 'ls -l /var/log'
    run_system_command(cmd)
