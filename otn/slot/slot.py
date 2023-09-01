import click
from . import edfa, terminal_line_show, voa, ocm, otdr, osc, olp, wss, port, slot_upgrade, terminal_client_show, terminal_client_config, terminal_line_config
from otn.utils.utils import *
from otn.utils.config_utils import set_slot_configuration_save, set_slot_synchronized_save
from otn.utils.db import *
from otn.utils.pm import *
from otn.utils.thrift import *

CARD_TYPE_NONE = "NONE"
OBX_TERMINAL_LINECARD = ['P230C']
OBX1100_CARD_TYPE_LIST = ['P230C','E110C','E100C','E120C']
OBX2000_CARD_TYPE_LIST = ['OCM8','OTDR8','OA2325','OA2335','OA2125','OA2135','WSS9OA2125','WSS9OA2135']
CARD_TYPE_LIST = OBX1100_CARD_TYPE_LIST + OBX2000_CARD_TYPE_LIST

BOARD_MODE_STRING=['L1_400G_CA_100GE', 'LA_200G_CA_100GE_QPSK', 'LA_400G_CA_200GE']
#################################### info ############################################################
@click.group()
@click.pass_context
@click.argument('slot_idx',type=DynamicModuleIdxChoice('slot'), required=True)
def slot(ctx, slot_idx):
    ctx.obj['slot_idx'] = int(slot_idx)
    load_slot_capability(ctx, slot_idx)

@slot.command()
@click.pass_context
def info(ctx):
    show_slot_info_impl(ctx.obj['slot_idx'])

@slot.command()
@click.pass_context
def config(ctx):
    show_slot_config_impl(ctx.obj['slot_idx'])

#################################### alarm ############################################################
@slot.group()
@click.pass_context
def alarm(ctx):
    pass

@alarm.command()
@click.pass_context
def current(ctx):
    show_slot_alarm_current(ctx.obj['slot_idx'])

@alarm.command()
@click.pass_context
def history(ctx):
    show_slot_alarm_history(ctx.obj['slot_idx'])
        
slot.add_command(slot_upgrade.show_slot_upgrade)
slot.add_command(edfa.edfa)
slot.add_command(voa.voa)
slot.add_command(ocm.ocm)
slot.add_command(otdr.otdr)
slot.add_command(osc.osc)
slot.add_command(olp.olp)
slot.add_command(wss.wss)
slot.add_command(port.port)
slot.add_command(terminal_client_show.client)
slot.add_command(terminal_line_show.line)
#################################### pm ############################################################
@slot.group()
@click.pass_context
@click.argument('pm_type',type=click.Choice(['15','24']),required=True)
def pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@pm.command()
@click.pass_context
def current(ctx):
    slot_id = ctx.obj['slot_idx']
    show_slot_pm_current_impl(slot_id, "LINECARD", ctx.obj['pm_type'])
    
@pm.command()
@click.pass_context
@click.argument('bin_idx',type=click.IntRange(1, 96),required=True)
def history(ctx, bin_idx):
    slot_id = ctx.obj['slot_idx']
    show_slot_pm_history_impl(slot_id, "LINECARD", ctx.obj['pm_type'], bin_idx)

#####################################config########################################################
@click.group("slot")
@click.pass_context
@click.argument('slot_idx',type=DynamicModuleIdxChoice('slot'), required=True)
def cfg_slot(ctx, slot_idx):
    ctx.obj['slot_idx'] = int(slot_idx)
    load_slot_capability(ctx, slot_idx)

@cfg_slot.command()
@click.argument('power_mode',type=click.Choice(['on', 'off']), required=True)
@click.pass_context
def power(ctx, power_mode):
    slot_id = ctx.obj['slot_idx']
    value_dict = {'on':1, 'off':0}
    value = value_dict[power_mode]
    thrift_set_slot_power(slot_id,value)

@cfg_slot.group('temperature-threshold')
@click.pass_context
def temeprature_threshold(ctx):
    pass

@temeprature_threshold.group('low-alarm')
@click.argument('la_value',type=DynamicFieldFloatRange('slot_temp_low_alarm_threshold'),required=True)
@click.pass_context
def low_alarm(ctx,la_value):
    ctx.obj['la_value'] = la_value

@low_alarm.group('low-warning')
@click.argument('lw_value',type=DynamicFieldFloatRange('slot_temp_low_warning_threshold'),required=True)
@click.pass_context
def low_warning(ctx,lw_value):
    ctx.obj['lw_value'] = lw_value

@low_warning.group('hi-alarm')
@click.argument('ha_value',type=DynamicFieldFloatRange('slot_temp_hi_alarm_threshold'),required=True)
@click.pass_context
def hi_alarm(ctx,ha_value):
    ctx.obj['ha_value'] = ha_value

@hi_alarm.command('hi-warning')
@click.argument('hw_value',type=DynamicFieldFloatRange('slot_temp_hi_warning_threshold'),required=True)
@click.pass_context
def hi_warning(ctx,hw_value):
    slot_id = ctx.obj['slot_idx']
    la_value = ctx.obj['la_value']
    lw_value = ctx.obj['lw_value']
    ha_value = ctx.obj['ha_value']
    
    if ha_value < hw_value:
        click.echo(f"Error, high alarm threshold should be greater than high warning threshold.")
        return
    
    if la_value > lw_value:
        click.echo(f"Error, low alarm threshold should be less than low warning threshold.")
        return
                   
    config_slot(slot_id, "temp-low-alarm-threshold", la_value) 
    config_slot(slot_id, "temp-low-warn-threshold", lw_value) 
    config_slot(slot_id, "temp-high-alarm-threshold", ha_value) 
    config_slot(slot_id, "temp-high-warn-threshold", hw_value)
    click.echo('Successed')
    
@cfg_slot.group("console")
@click.pass_context
def console_cfg(ctx):
    pass

@console_cfg.command("baudrate")
@click.argument('baudrate_value',type=click.Choice(['9600','19200','38400','57600','115200']),required=True)
@click.pass_context
def slot_baudrate_cfg(ctx,baudrate_value):
    slot_id = ctx.obj['slot_idx']
    set_slot_synchronized_save(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'baud-rate', baudrate_value)
    click.echo('Successed')
       
@cfg_slot.command('type')
@click.argument('cfg_type',type=click.Choice(CARD_TYPE_LIST+[CARD_TYPE_NONE]),required=True)
@click.argument('board_mode',type=click.Choice(BOARD_MODE_STRING),required=False,default='L1_400G_CA_100GE')
@click.pass_context
def card_type(ctx,cfg_type,board_mode):
    slot_id = ctx.obj['slot_idx']
    
    try:
        if cfg_type in OBX_TERMINAL_LINECARD:
            config_terminal_linecard(slot_id, cfg_type, board_mode)
            click.echo('Successed')
        elif cfg_type in CARD_TYPE_LIST:
            config_optical_linecard(slot_id, cfg_type)
            click.echo('Successed')
        elif cfg_type == CARD_TYPE_NONE:
            config_linecard_type_none(slot_id)
            click.echo('Successed')
        else:
            click.echo(f'Error, Invalid linecard type {cfg_type}')
    except Exception as e:
        click.echo(e)

#################################### clear ############################################################
@cfg_slot.command("clear-alarm")
@click.pass_context
def clear_alarm(ctx):
    clear_slot_alarm(ctx.obj['slot_idx'])
    
#################################### clear pm ############################################################
@cfg_slot.group("clear-pm")
@click.argument('pm_type',type=click.Choice(['15','24', 'all']),required=True)
@click.pass_context
def clear_pm(ctx, pm_type):
    ctx.obj['pm_type'] = pm_type

@clear_pm.command()
@click.pass_context
def current(ctx):
    slot_id = ctx.obj['slot_idx']
    pm_type = ctx.obj['pm_type']
    table_key = f'LINECARD:LINECARD-1-{slot_id}'
    state_db = get_state_db_by_slot(slot_id)
    set_table_field(state_db, "CLEANPM",table_key,'period', pm_type)
    click.echo('Successed')
                
cfg_slot.add_command(slot_upgrade.slot_upgrade)
cfg_slot.add_command(edfa.cfg_edfa)
cfg_slot.add_command(voa.cfg_voa)
# cfg_slot.add_command(ocm.cfg_ocm)
# cfg_slot.add_command(otdr.cfg_otdr)
cfg_slot.add_command(osc.cfg_osc)
cfg_slot.add_command(olp.cfg_olp)
# cfg_slot.add_command(wss.cfg_wss)
cfg_slot.add_command(port.cfg_port)
cfg_slot.add_command(terminal_client_config.cfg_client)
cfg_slot.add_command(terminal_line_config.cfg_line)

#####################################switch########################################################
@click.group()
def switch():
    pass

@switch.command('slot')
@click.argument('slot_idx',type=DynamicModuleIdxChoice('slot'), required=True)
def switch_slot(slot_idx):
    run_slot_cli_comand(slot_idx, 'show version')
       
#################################################################################################
def show_slot_info_impl(slot_id):
    table_name = "LINECARD"
    show_slot_info(slot_id, table_name)
    show_slot_pm_instant(slot_id, PM_LIST, table_name)
    
def show_slot_info(slot_id, table_name):
    table_key = f'{table_name}-1-{slot_id}'
    db = get_state_db_by_slot(slot_id)
    dict_kvs = get_db_table_fields(db, table_name, table_key)
    show_key_value_list(STATE_LIST,dict_kvs)

def show_slot_config(slot_id, table_name):
    table_key = f'{table_name}-1-{slot_id}'
    db = get_config_db_by_slot(slot_id)
    dict_kvs = get_db_table_fields(db, table_name, table_key)
    show_key_value_list(CONFIG_LIST,dict_kvs)
    
def show_slot_config_impl(slot_id):
    table_name = "LINECARD"
    show_slot_config(slot_id, table_name)
 
def show_slot_pm_instant(slot_id, pm_list, table_name):
    section_str = ""
    db = get_counter_db_by_slot(slot_id)
    for field in pm_list:
        table_key = f"{table_name}-1-{slot_id}_{field['Field']}:15_pm_current"
        value = get_pm_instant(db, table_name, table_key)
        key = field['show_name']
        section_str += key.ljust(FIELD_WITH)+ ": " + value + "\n"
    click.echo(section_str)

def show_slot_pm_current_impl(slot_id, table_name, pm_type):
    show_slot_pm_current_head(slot_id, table_name, pm_type)
    show_slot_pm_current(slot_id, PM_LIST, table_name, pm_type)

def show_slot_pm_history_impl(slot_id, table_name, pm_type, bin_idx):
    show_slot_pm_history_head(slot_id, table_name, pm_type, bin_idx)
    show_slot_pm_history(slot_id, PM_LIST, table_name, pm_type, bin_idx)

def config_slot(slot_id, field, value):
    table_name = 'LINECARD'
    table_key = f'LINECARD-1-{slot_id}'
    set_slot_configuration_save(slot_id,table_name,table_key,field, value)

def flush_linecard_data(slot_id):
    for db_id in DB_IDX_LIST:
        connect_muti_db_common(slot_id, db_id).flushdb()
    db = get_config_db_by_slot(slot_id)
    db.set("CONFIG_DB_INITIALIZED", 1)

    run_command(f"rm  -f /etc/sonic/redis{slot_id-1}/dump.rdb")
    run_command(f"rm  -f /etc/sonic/config_db{slot_id-1}.json")
    time.sleep(0.5)

def flush_terminal_linecard_data(slot_id):
    state_db = get_state_db_by_slot(slot_id)
    flush_db_except_table_key(state_db, "LINECARD", f"LINECARD-1-{slot_id}", "|")
    flush_linecard_data(slot_id)

def flush_none_terminal_linecard_data(slot_id):
    state_db = get_state_db_by_slot(slot_id)
    flush_db_except_table_key_fields(state_db, "LINECARD", f"LINECARD-1-{slot_id}", "|", ["power-admin-state","empty"])
    flush_linecard_data(slot_id)

def create_linecard_config_file(slot_id, cfg_type):
    cmd = f'sudo python3 /usr/sbin/recover_default_config.py  slot {slot_id} type {cfg_type.lower()} force > /var/log/recover_default_slot{slot_id}.log'
    run_command(cmd)

def create_terminal_linecard_config(slot_id, cfg_type, board_mode):
    cmd = f"sudo ln -sf /etc/sonic/factory/{cfg_type.lower()}/{board_mode}/config_db{slot_id-1}.json /etc/sonic/factory/{cfg_type.lower()}/config_db{slot_id-1}.json"
    run_command(cmd)

def config_linecard_type_none(slot_id):
    log.log_info(f"real state: {is_slot_present(slot_id)} {is_card_type_mismatch(slot_id)}") 
    if not is_slot_present(slot_id) or is_card_type_mismatch(slot_id):
        flush_none_terminal_linecard_data(slot_id)
    else:
        echo_log_exit("Error: Cannot config cardtype NONE if linecard present and type matched.")

def config_optical_linecard(slot_id, cfg_type):
    log.log_info(f"real state: {is_slot_present(slot_id)} {get_slot_card_type(slot_id)}")       
    if is_emtpty_slot_without_cardtype(slot_id):
        flush_none_terminal_linecard_data(slot_id)
        click.echo(f'Setting card {slot_id} type {cfg_type} now, Wait for a minute..')
        create_linecard_config_file(slot_id, cfg_type)
        set_slot_synchronized_save(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'linecard-type', cfg_type)
    else:
        echo_log_exit("Error: Please remove the linecard and config cardtype to NONE first.")

def is_emtpty_slot_without_cardtype(slot_id):
    return not is_slot_present(slot_id) and get_slot_card_type(slot_id) == NA_VALUE

def is_terminal_linecard_update_boardmode(slot_id, cfg_type, board_mode):
    real_board_mode = get_slot_board_mode(slot_id)
    return is_slot_present(slot_id) and slot_is_ready(slot_id) \
        and cfg_type in OBX_TERMINAL_LINECARD and NA_VALUE != real_board_mode \
        and board_mode != real_board_mode

def config_terminal_linecard(slot_id, cfg_type, board_mode): 
    log.log_info(f"real state: {is_slot_present(slot_id)} {get_slot_card_type(slot_id)} {slot_is_ready(slot_id)} {get_slot_board_mode(slot_id)}")       
    if is_emtpty_slot_without_cardtype(slot_id) \
        or is_terminal_linecard_update_boardmode(slot_id, cfg_type, board_mode):
            log.log_info(f"Config slot {slot_id} {cfg_type} {board_mode}, real {is_slot_present(slot_id)}")
            flush_terminal_linecard_data(slot_id)
            create_terminal_linecard_config(slot_id, cfg_type, board_mode)
            click.echo(f'Setting card {slot_id} type {cfg_type} board-mode {board_mode} now, Wait for a minute..')
            create_linecard_config_file(slot_id, cfg_type)
    else:
        if not is_terminal_linecard_update_boardmode(slot_id, cfg_type, board_mode):
            echo_log_exit("Error: The linecard is running, and board mode is not changed.")
        else:
            echo_log_exit("Error: Please remove the linecard and config cardtype to NONE first.")

def clear_slot_alarm(slot_id):
    db = get_history_db_by_slot(slot_id)
    patterns = ["HISALARM:*", "HISEVENT:*"]
    for pattern in patterns:
        clear_db_entity_alarm_history(db, pattern)
    click.echo("Succeed")

STATE_LIST = [
    {'Field': 'linecard-type',              'show_name': 'Card Type'},
    {'Field': 'board-mode',                 'show_name': 'Board mode'},
    {'Field': 'admin-state',                'show_name': 'Admin'},
    {'Field': 'oper-status',                'show_name': 'Oper Status'},
    {'Field': 'part-no',                    'show_name': 'Part no'},
    {'Field': 'serial-no',                  'show_name': 'Serial no'},
    {'Field': 'hardware-version',           'show_name': 'Hardware ver'},
    {'Field': 'software-version',           'show_name': 'Software ver'},
    {'Field': 'mfg-name',                   'show_name': 'Mfg name'},
    {'Field': 'mfg-date',                   'show_name': 'Mfg date'},
    {'Field': 'led-color',                  'show_name': 'Alarm Led State'},
]

CONFIG_LIST = [
    {'Field': 'linecard-type',              'show_name': 'Card Type'},
    {'Field': 'board-mode',                 'show_name': 'Board mode'},
    {'Field': 'admin-state',                'show_name': 'Admin'},
    {'Field': 'baud-rate',                  'show_name': 'Baudrate'},
    {'Field': 'hostname',                   'show_name': 'Hostname'},
    {'Field': 'temp-high-alarm-threshold',  'show_name': 'Temp Hi-Alarm(C)'},
    {'Field': 'temp-high-warn-threshold',   'show_name': 'Temp Hi-Warning(C)'},
    {'Field': 'temp-low-alarm-threshold',   'show_name': 'Temp Low-Alarm(C)'},
    {'Field': 'temp-low-warn-threshold',    'show_name': 'Temp Low-Warning(C)'},
]

PM_LIST = [
    {'Field': 'Temperature',                'show_name': 'Temperature(C)'},
    {'Field': 'CpuUtilization',             'show_name': 'CPU utilized(%)'},
    {'Field': 'MemoryAvailable',            'show_name': 'Memory available(B)'},
    {'Field': 'MemoryUtilized',             'show_name': 'Memory utilized(B)'},
]