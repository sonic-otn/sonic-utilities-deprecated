import click
import sys
from otn.utils.utils import *
from otn.utils.db import *
from otn.utils.pm import *
# TODO replace with pmon.otn.public
from otn.utils.thrift import thrift_clear_psu_pm

################################### show #########################################################
@click.group()
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('psu'))
def psu(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'psu'
       
@psu.command()
@click.pass_context
def info(ctx):
    psu_ids = get_module_ids(ctx)
    show_psus_info(psu_ids)

#################################### pm ############################################################
@psu.group()
@click.pass_context
@click.argument('pm_type',type=click.Choice(['15','24']),required=True)
def pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@pm.command()
@click.pass_context
def current(ctx):
    psu_ids = get_module_ids(ctx)
    show_psus_pm_current(psu_ids, ctx.obj['pm_type'])
    
@pm.command()
@click.pass_context
@click.argument('bin_idx',type=click.IntRange(1, 96),required=True)
def history(ctx, bin_idx):
    psu_ids = get_module_ids(ctx)
    show_psus_pm_history(psu_ids, ctx.obj['pm_type'], bin_idx)
#################################### clear pm ############################################################
@click.group("psu")
@click.pass_context
@click.argument('module_idx',type=DynamicModuleIdxAllChoice('psu'))
def cfg_psu(ctx, module_idx):
    ctx.obj['module_idx'] = module_idx
    ctx.obj['module_type'] = 'psu'

@cfg_psu.group("clear-pm")
@click.argument('pm_type',type=click.Choice(['15','24', 'all']),required=True)
@click.pass_context
def clear_pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@clear_pm.command()
@click.pass_context
def current(ctx):
    psu_ids = get_module_ids(ctx)
    pm_type = ctx.obj['pm_type']
    for psu_id in psu_ids:
        thrift_clear_psu_pm(psu_id, pm_type)
    click.echo('Succeeded')


################################################################################################
def show_psu_info(psu_id):
    table_name = "PSU"
    show_psu_info_impl(psu_id, table_name)
    show_psu_pm_instant(psu_id, PM_LIST, table_name)
    
def show_psus_info(psu_ids):
    for psu_id in psu_ids:
        show_psu_info(psu_id)

def show_psu_info_impl(psu_id, table_name):
    table_key = f'{table_name}-1-{psu_id}'
    db = get_chassis_state_db()
    dict_kvs = get_db_table_fields(db, table_name, table_key)
    click.echo("Name".ljust(FIELD_WITH)+ ": " + table_key)
    show_key_value_list(STATE_LIST,dict_kvs)
    
def show_psu_pm_instant(psu_id, pm_list, table_name):
    section_str = ""
    db = get_chassis_counter_db()
    for field in pm_list:
        table_key = f"{table_name}-1-{psu_id}_{field['Field']}:15_pm_current"
        value = get_pm_instant(db, table_name, table_key)
        key = field['show_name']
        section_str += key.ljust(FIELD_WITH)+ ": " + value + "\n"
    click.echo(section_str)

def show_psus_pm_current(psu_ids, pm_type):
    for psu_id in psu_ids:
        show_psu_pm_current_impl(psu_id, pm_type)

def show_psu_pm_current_impl(psu_id, pm_type):
    show_entity_pm_current_head(f"PSU-1-{psu_id}", pm_type)
    show_psu_pm_current(psu_id, PM_LIST, "PSU", pm_type)

def show_psus_pm_history(psu_ids, pm_type, bin_idx):
    for psu_id in psu_ids:
        show_psu_pm_history_impl(psu_id, pm_type, bin_idx)

def show_psu_pm_history_impl(psu_id, pm_type, bin_idx):
    show_entity_pm_history_head(f"PSU-1-{psu_id}", pm_type, bin_idx)
    show_psu_pm_history(psu_id, PM_LIST, "PSU", pm_type, bin_idx)

STATE_LIST = [
    {'Field': 'part-no',                    'show_name': 'Part no'},
    {'Field': 'serial-no',                  'show_name': 'Serial no'},
    {'Field': 'hardware-version',           'show_name': 'Hardware ver'},
    {'Field': 'mfg-name',                   'show_name': 'Mfg name'},
    {'Field': 'mfg-date',                   'show_name': 'Mfg date'},
    {'Field': 'capacity',                   'show_name': 'Capacity'},
    {'Field': 'ambient-temp',               'show_name': 'Ambient Temp(C)'},
]

PM_LIST = [
    {'Field': 'Temperature',                'show_name': 'Temperature(C)'},
    {'Field': 'InputCurrent',               'show_name': 'Input Current(A)'},
    {'Field': 'OutputCurrent',              'show_name': 'Output Current(A)'},
    {'Field': 'InputVoltage',               'show_name': 'Input Voltage(V)'},
    {'Field': 'OutputVoltage',              'show_name': 'Output Voltage(V)'},
    {'Field': 'OutputPower',                'show_name': 'Output Power(W)'},
]