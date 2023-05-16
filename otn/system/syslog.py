import click
from tabulate import tabulate
from sonic_py_common import device_info
from otn.utils.utils import is_ipaddress, run_command
from otn.utils.db import *
from otn.utils.config_utils import set_chassis_configuration_save, delete_chassis_configuration_save

@click.group()
def syslog():
    pass
    
@syslog.command()
def server():
    syslog_servers = []
    with open("/etc/rsyslog.conf") as syslog_file:
        data = syslog_file.readlines()
    for line in data:
        if line.startswith("*.* @"):
            line = line.split(":")
            server = line[0][6:-1]
            syslog_servers.append([server])
    print(tabulate(syslog_servers, headers=['Syslog Servers'], tablefmt="simple", stralign='left', missingval=""))

@click.group("syslog")
@click.pass_context
def syslog_cfg(ctx):
    pass

@syslog_cfg.group("server")
@click.pass_context
def server_cfg(ctx):
    pass

@server_cfg.command('add')
@click.argument('syslog_ip_address', metavar='<syslog_ip_address>', required=True)
@click.argument('syslog_severity', metavar='(emerg|alert|crit|err|warn|notice|info|debug|all)', 
                type=click.Choice(['emerg', 'alert', 'crit', 'err', 'warn', 'notice', 'info', 'debug', 'all']),
                required=False, default='all')
@click.pass_context
def add_syslog_server(ctx, syslog_ip_address, syslog_severity):
    """ Add syslog server IP """
    if not is_ipaddress(syslog_ip_address):
        click.echo(f'Error, Invalid ip address {syslog_ip_address}')
        return
    db = get_chassis_config_db()
    syslog_servers = get_db_table_keys(db, "SYSLOG_SERVER")
    if syslog_ip_address in syslog_servers:
        click.echo(f"Error, Syslog server {syslog_ip_address} is already configured")
        return
    
    set_chassis_configuration_save('SYSLOG_SERVER', syslog_ip_address, 'severity', syslog_severity)
    device_info.add_loopbackrule(syslog_ip_address)
    
    try:
        run_command("systemctl restart rsyslog-config")
        click.echo('Succeeded')
    except SystemExit as e:
        click.echo(f"Error, Restart service rsyslog-config failed with error {e}")


@server_cfg.command('delete')
@click.argument('syslog_ip_address', metavar='<syslog_ip_address>', required=True)
@click.pass_context
def del_syslog_server(ctx, syslog_ip_address):
    """ Delete syslog server IP """
    if not is_ipaddress(syslog_ip_address):
        click.echo(f'Error, Invalid IP address {syslog_ip_address}')
        return
        
    db = get_chassis_config_db()
    syslog_servers = get_db_table_keys(db, "SYSLOG_SERVER")
    if syslog_ip_address in syslog_servers:
        delete_chassis_configuration_save('SYSLOG_SERVER', syslog_ip_address)
        device_info.del_loopbackrule(syslog_ip_address)
    else:
        click.echo("Error, Syslog server {} is not configured.".format(syslog_ip_address))
        return
    
    try:
        run_command("systemctl restart rsyslog-config")
        click.echo('Succeeded')
    except SystemExit as e:
        click.echo(f"Error, Restart service rsyslog-config failed with error {e}")
