import click
from otn.utils.db import *

TELEMETRY_TABLE = 'TELEMETRY_CLIENT'

@click.group()
def telemetry():
    pass

@telemetry.command()
def info():
    cfg_db = get_chassis_config_db()
    pattern = TELEMETRY_TABLE + "|" + "DestinationGroup_*"
    display_destinations(cfg_db, cfg_db.keys(pattern))

    pattern = TELEMETRY_TABLE + "|" + "Subscription_*"
    display_sensor_group(cfg_db, cfg_db.keys(pattern))

def display_sensor_group(db, table_keys):
    if len(table_keys) != 0 :
        click.echo('sensor-groups :')
    for table_key in table_keys:
        key_list = table_key.split("|")
        group_id = key_list[1]
        if group_id.find('_') > 0:
            group_id = group_id[group_id.find('_') + 1:]
        print('  group-id : {group_id}'.format(group_id = group_id))
        dict_data = get_db_table_fields(db, TELEMETRY_TABLE, key_list[1])
        print('    heartbeat-interval : {value}'.format(value = dict_data['heartbeat_interval']))
        print('    sample-interval    : {value}'.format(value = dict_data['report_interval']))
        print('    paths              : {value}'.format(value = dict_data['paths']))

def display_destinations(db, table_keys):
    for table_key in table_keys:
        key_list = table_key.split("|")
        dict_data = get_db_table_fields(db, TELEMETRY_TABLE, key_list[1])
        print('destinations  : {value}'.format(value=dict_data['dst_addr']))