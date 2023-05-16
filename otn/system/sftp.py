
import click
import os
from sonic_py_common import device_info
from otn.utils.classsftp import Pysftp

@click.command('sftpget')
@click.argument("ip_addr", metavar="<ip_addr>", required=True)
@click.argument('port',type=click.IntRange(0,65535),required=False,default=22)
@click.argument('remote_file',type=str,required=True)
@click.argument('local_file',type=str,required=False)
@click.argument('uname',type=str,required=True)
@click.password_option(confirmation_prompt=False)
def sftpget(ip_addr, port, remote_file, local_file, uname, password):
    try:
        sftp_get_file(ip_addr, port, uname, password, local_file, remote_file)
        click.echo('Succeeded')
    except Exception as e:
        click.echo(e)

@click.command('sftpput')
@click.argument("ip_addr", metavar="<ip_addr>", required=True)
@click.argument('port',type=click.IntRange(0,65535),required=False,default=22)
@click.argument('local_file',type=str,required=True)
@click.argument('remote_file',type=str,required=True)
@click.argument('uname',type=str,required=True)
@click.password_option(confirmation_prompt=False)
def sftpput(ip_addr, port, local_file, remote_file, uname, password):
    try:
        sftp_put_file(ip_addr, port, uname, password, local_file, remote_file)
        click.echo('Succeeded')
    except Exception as e:
        click.echo(e)
        
def sftp_get_file(ip_addr, port, uname, password, local_file, remote_file):
    try:
        device_info.add_loopbackrule(ip_addr)
        sftp = Pysftp(ip_addr, port, uname, password, local_file, remote_file)
        if sftp.connect() != True:
            raise Exception("Error: failed to connect")
        if sftp.get() != True:
            raise Exception(f'Error: failed to get file')
        if not os.path.exists(local_file):
            raise Exception(f'Error: failed to get {remote_file}.')
    finally:
        device_info.del_loopbackrule(ip_addr)

def sftp_put_file(ip_addr, port, uname, password, local_file, remote_file):
    try:
        device_info.add_loopbackrule(ip_addr)
        sftp = Pysftp(ip_addr, port, uname, password, local_file, remote_file)
        if sftp.connect() != True:
            raise Exception(f'Error: failed to connect')
        if sftp.put() != True:
            raise Exception(f'Error: failed to put file')
    finally:
        device_info.del_loopbackrule(ip_addr)