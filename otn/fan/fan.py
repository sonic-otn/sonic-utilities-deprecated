import click
import sys
from otn.utils.utils import *
from otn.utils.db import *
from otn.utils.pm import *
# TODO replace with pmon.otn.public
from otn.utils.thrift import *

################################### show #########################################################
@click.group()
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('fan'))
def fan(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'fan'
       
@fan.command()
@click.pass_context
def info(ctx):
    fan_ids = get_module_ids(ctx)
    show_fans_info(fan_ids)

#################################### pm ############################################################
@fan.group()
@click.pass_context
@click.argument('pm_type',type=click.Choice(['15','24']),required=True)
def pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@pm.command()
@click.pass_context
def current(ctx):
    fan_ids = get_module_ids(ctx)
    show_fans_pm_current(fan_ids, ctx.obj['pm_type'])
    
@pm.command()
@click.pass_context
@click.argument('bin_idx',type=click.IntRange(1, 96),required=True)
def history(ctx, bin_idx):
    fan_ids = get_module_ids(ctx)
    show_fans_pm_history(fan_ids, ctx.obj['pm_type'], bin_idx)
#################################### config ############################################################
@click.group("fan")
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('fan'))
def cfg_fan(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'fan'

@cfg_fan.command()
@click.argument('speed',type=str,required=True)
@click.pass_context
def speed(ctx, speed):
    fan_ids = get_module_ids(ctx)
    config_fans_speed(fan_ids, speed)

#################################### clear pm ############################################################
@cfg_fan.group("clear-pm")
@click.pass_context
@click.argument('pm_type',type=click.Choice(['15','24', 'all']),required=True)
def clear_pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@clear_pm.command()
@click.pass_context
def current(ctx):
    fan_ids = get_module_ids(ctx)
    pm_type = ctx.obj['pm_type']
    for fan_id in fan_ids:
        thrift_clear_fan_pm(fan_id, pm_type)
    click.echo('Succeeded')

################################################################################################
def show_fan_info(fan_id):
    table_name = "FAN"
    show_fan_info_impl(fan_id, table_name)
    show_fan_pm_instant(fan_id, PM_LIST, table_name)
    
def show_fans_info(fan_ids):
    for fan_id in fan_ids:
        show_fan_info(fan_id)

def show_fan_info_impl(fan_id, table_name):
    table_key = f'{table_name}-1-{fan_id}'
    db = get_chassis_state_db()
    dict_kvs = get_db_table_fields(db, table_name, table_key)
    click.echo("Name".ljust(FIELD_WITH)+ ": " + table_key)
    show_key_value_list(STATE_LIST,dict_kvs)
    
def show_fan_pm_instant(fan_id, pm_list, table_name):
    section_str = ""
    db = get_chassis_counter_db()
    for field in pm_list:
        table_key = f"{table_name}-1-{fan_id}_{field['Field']}:15_pm_current"
        value = get_pm_instant(db, table_name, table_key)
        key = field['show_name']
        section_str += key.ljust(FIELD_WITH)+ ": " + value + "\n"
    click.echo(section_str)

def show_fans_pm_current(fan_ids, pm_type):
    for fan_id in fan_ids:
        show_fan_pm_current_impl(fan_id, pm_type)

def show_fan_pm_current_impl(fan_id, pm_type):
    show_entity_pm_current_head(f"FAN-1-{fan_id}", pm_type)
    show_fan_pm_current(fan_id, PM_LIST, "FAN", pm_type)

def show_fans_pm_history(fan_ids, pm_type, bin_idx):
    for fan_id in fan_ids:
        show_fan_pm_history_impl(fan_id, pm_type, bin_idx)

def show_fan_pm_history_impl(fan_id, pm_type, bin_idx):
    show_entity_pm_history_head(f"FAN-1-{fan_id}", pm_type, bin_idx)
    show_fan_pm_history(fan_id, PM_LIST, "FAN", pm_type, bin_idx)
    
def config_fan_speed(fan_id, speed):
    return thrift_config_fan_speed(fan_id, speed)

def config_fans_speed(fan_ids, speed):
    if not is_valide_speed(speed):
        click.echo("Failed. Invalid parameter speed")
        return

    for fan_id in fan_ids:
        config_fan_speed(fan_id, speed)         
    click.echo('Succeeded')
    
def is_valide_speed(speed):
    if 'auto' == speed:
        return True
    else:
        return speed.isnumeric()

STATE_LIST = [
    {'Field': 'part-no',                    'show_name': 'Part no'},
    {'Field': 'serial-no',                  'show_name': 'Serial no'},
    {'Field': 'hardware-version',           'show_name': 'Hardware ver'},
    {'Field': 'mfg-name',                   'show_name': 'Mfg name'},
    {'Field': 'mfg-date',                   'show_name': 'Mfg date'},
]

PM_LIST = [
    {'Field': 'Temperature',                'show_name': 'Temperature(C)'},
    {'Field': 'Speed',                      'show_name': 'Speed1(RPM)'},
    {'Field': 'Speed_2',                    'show_name': 'Speed2(RPM)'},
]