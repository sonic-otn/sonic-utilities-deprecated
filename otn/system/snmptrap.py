import click

from tabulate import tabulate
from otn.utils.utils import *
from otn.utils.config_utils import set_chassis_multi_configuration_save, delete_chassis_configuration_save

@click.command()
@click.pass_context
def snmptrap(ctx):
    db = get_chassis_config_db()
    table_name = 'SNMP_TRAP_SERVER'
    keys = get_db_table_keys(db, table_name)
    header = ['id', 'version', 'address', 'port']
    body = []   
    for key in keys:
        info_data = get_db_table_fields(db, table_name, key)
        body.append([info_data['id'], info_data['version'], info_data['address'], info_data['port']])
        
    click.echo(tabulate(body, header))

@click.group("snmptrap")
@click.pass_context
def snmptrap_cfg(ctx):
    pass

@snmptrap_cfg.group()
@click.pass_context
def add(ctx):
    pass

@add.command("server")
@click.argument('sid', type=click.IntRange(1, 3), metavar='<snmp_trap_sever_id>', required=True)
@click.argument('address', metavar='<snmp_trap_ip_address>', required=True)
@click.argument('port', metavar='<snmp_trap_ip_port>', default=162)
@click.pass_context
def add_snmptrap_server(ctx, sid, address, port):    
    if not is_ipaddress(address):
        click.echo(f'Error, Invalid ip address {address}')
        return
    
    sid = str(sid)
    db = get_chassis_config_db()    
    server_ids = get_db_table_keys(db, "SNMP_TRAP_SERVER")
    if sid in server_ids:
        click.echo(f"Error, snmp server id {sid} is already configured")
        return
    
    data = [('id', sid), ('port', '123'), ('version', 'v2'), ('address', address), ('port', str(port))]
    set_chassis_multi_configuration_save('SNMP_TRAP_SERVER', sid, data)
    click.echo('Succeeded')
    
@snmptrap_cfg.group()
@click.pass_context
def delete(ctx):
    pass

@delete.command('server')
@click.argument('sid', type=click.IntRange(1, 3), metavar='<snmp_trap_sever_id>', required=True)
@click.pass_context
def delete_snmptrap_server(ctx, sid):
    delete_chassis_configuration_save('SNMP_TRAP_SERVER', str(sid))
    click.echo('Succeeded')
