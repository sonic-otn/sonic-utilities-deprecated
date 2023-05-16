import click

from sonic_py_common import device_info
from otn.utils.db import *
from otn.utils.config_utils import *
from otn.utils.utils import *

@click.command()
@click.pass_context
def ntp(ctx):
    db = get_chassis_config_db()
    enable = get_db_table_field(db, 'NTP', 'global', 'enabled')
    if enable == 'true':
        run_command("chronyc sources")
        return
    click.echo("NTP state is disabled")

@click.group("ntp")
@click.pass_context
def ntp_cfg(ctx):
    pass

@ntp_cfg.command()
@click.pass_context
def enable(ctx):
    set_chassis_configuration_save('NTP','global','enabled', 'true')
    click.echo('Succeeded')

@ntp_cfg.command()
@click.pass_context
def disable(ctx):
    set_chassis_configuration_save('NTP','global','enabled', 'false')
    click.echo('Succeeded')

@ntp_cfg.command('add')
@click.argument('ntp_ip_address', metavar='<ntp_ip_address>', required=True)
@click.argument('prefer', metavar='<prefer>', type=click.Choice(['prefer']), required=False)
@click.pass_context
def add_ntp_server(ctx, ntp_ip_address, prefer):
    """ Add NTP server IP """
    if not is_ipaddress(ntp_ip_address):
        click.echo(f'Error, Invalid ip address {ntp_ip_address}')
        return
        
    db = get_chassis_config_db()
    ntp_servers = get_db_table_keys(db, "NTP_SERVER")
    if ntp_ip_address in ntp_servers:
        click.echo(f"Error, NTP server {ntp_ip_address} is already configured")
        return
    
    for ntp_server in ntp_servers:
        prefer_value = get_db_table_field(db, "NTP_SERVER", ntp_server, 'prefer')
        if prefer_value == 'true':
            click.echo(f"Error, NTP server {ntp_server} is already used as prefer")
            return

    perfer_config = 'false' if not prefer else 'true'
    data = [('address', ntp_ip_address), ('port', '123'), ('version', '4'), ('iburst', 'false'), ('association-type', 'SERVER'), ('prefer', perfer_config)]
    set_chassis_multi_configuration_save('NTP_SERVER', ntp_ip_address, data)
    device_info.add_loopbackrule(ntp_ip_address)
    click.echo('Succeeded')

@ntp_cfg.command('delete')
@click.argument('ntp_ip_address', metavar='<ntp_ip_address>', required=True)
@click.pass_context
def del_ntp_server(ctx, ntp_ip_address):
    """ Delete NTP server IP """
    if not is_ipaddress(ntp_ip_address):
        click.echo('Invalid IP address')
        return
        
    db = get_chassis_config_db()
    ntp_servers = get_db_table_keys(db, "NTP_SERVER")
    if ntp_ip_address not in ntp_servers:
        click.echo("Error, NTP server {} is not configured.".format(ntp_ip_address))
        return
    
    delete_chassis_configuration_save('NTP_SERVER', ntp_ip_address)
    device_info.del_loopbackrule(ntp_ip_address)
    click.echo('Succeeded')
