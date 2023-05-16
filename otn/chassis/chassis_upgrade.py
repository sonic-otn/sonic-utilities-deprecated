import click
import time

from tabulate import tabulate
from .cu_upgrade import *
from enum import Enum
from otn.utils.utils import *
from otn.slot.slot_upgrade import *
from otn.system.sftp import sftp_get_file

ALARM_FILETRANS_FAIL    = "FILETRANS_FAIL"
ALARM_SWUPG_IP          = "SWUPG_IP"
ALARM_SWUPG_ACT         = "SWUPG_ACT"
ALARM_SWUPG_FAIL        = "SWUPG_FAIL"

EXPIRE_7_DAYS = 7 * 24 * 60 * 60#unit s

class UpgradAlarmEn(Enum):
    PACKET_UPGRADE_SFTP_NOT_REACH_E = 1
    PACKET_UPGRADE_SFTP_DOWNLOAD_FAIL_E = 2
    PACKET_UPGRADE_SFTP_DOWNLAOD_CHECKSUM_ERR_E = 3
    PACKET_UPGRADE_IN_PROGRESS_E = 4
    PACKET_UPGRADE_ACTIVE_E = 5
    PACKET_UPGRADE_FAIL_E = 6
          
#####################################upgrade########################################################
@click.group("upgrade")
@click.pass_context
def chassis_upgrade(ctx):
    pass

@chassis_upgrade.command('auto')
@click.argument("ip_addr", metavar="<ip_addr>", required=True)
@click.argument('port',type=click.IntRange(0,65535),required=False,default=22)
@click.argument('tar_file_name',type=str,required=True)
@click.argument('uname',type=str,required=True)
@click.password_option(confirmation_prompt=False)
@click.pass_context
def upgrade_auto(ctx, ip_addr, port, tar_file_name, uname, password):
    click.echo(f'Upgrade Auto Not Support.')

@chassis_upgrade.command('download')
@click.argument("ip_addr", metavar="<ip_addr>", required=True)
@click.argument('port',type=click.IntRange(0,65535),required=False,default=22)
@click.argument('tar_file_name',type=str,required=True)
@click.argument('uname',type=str,required=True)
@click.password_option(confirmation_prompt=False)
@click.pass_context
def chassis_upgrade_download(ctx, ip_addr, port, tar_file_name, uname, password):
    try:         
        file_basename = os.path.basename(tar_file_name)
        if not file_basename.endswith('.tar.gz'):
            click.echo("Download file extension must be .tar.gz")
            return
        file_extract_name = file_basename[:-7]

        sftp_get_file(ip_addr, port, uname, password, file_basename, tar_file_name)
    
        click.echo("Extracting file...")
        os.system(f'sudo mkdir -p /tmp/chassis_img')
        os.system(f'sudo tar -zxf {file_basename} -C /tmp/chassis_img')
        os.system(f'sudo mv /tmp/chassis_img/{file_extract_name}/* /tmp/chassis_img')
        
        update_cu_upgrade_state(DOWNLOAD_FINISH)
        check_slots_upgrade_status(IDLE)
        click.echo("Downloading file to slots...")
        invoke_slots_download(ctx)
    except Exception as e:
        report_upgrade_event(ALARM_FILETRANS_FAIL)     
        click.echo(e)
    finally:
        os.system(f'sudo rm -rf {file_basename}')
        os.system(f'sudo rm -rf /tmp/chassis_img/{file_extract_name}')

@chassis_upgrade.command("commit")
@click.pass_context
def chassis_upgrade_commit(ctx):
    try:
        check_slots_upgrade_status(DOWNLOAD_FINISH)
        report_upgrade_event(ALARM_SWUPG_IP)
        invoke_slots_upgrade_operation(ctx, slot_upgrade_commit)
        cu_image_name = get_cu_target_image()
        cu_upgrade_commit_impl(f"/tmp/chassis_img/{cu_image_name}")
    except Exception as e:
        report_upgrade_event(ALARM_SWUPG_FAIL) 
        click.echo(e)

@chassis_upgrade.command("reboot")
@click.pass_context
def chassis_upgrade_reboot(ctx):
    try:
       check_slots_upgrade_status(COMMIT_FINISH)
       invoke_slots_upgrade_operation(ctx, slot_upgrade_reboot) 
       report_upgrade_event(ALARM_SWUPG_ACT)
       os.system("cp /tmp/chassis_img/upgradecfg /host/aonos_installer/upgradecfg")
       ctx.invoke(cu_upgrade_reboot)
    except Exception as e:
        click.echo(e)
    finally:
        os.system(f'sudo rm -rf /tmp/chassis_img')

@chassis_upgrade.command('commit-pause')
@click.pass_context
def chassis_upgrade_commit_pause(ctx):
    try:
        check_slots_upgrade_status(COMMITING)
        invoke_slots_upgrade_operation(ctx, slot_upgrade_commit_pause)
        ctx.invoke(cu_upgrade_commit_pause)
    except Exception as e:
        click.echo(e)

@chassis_upgrade.command('commit-resume')
@click.pass_context
def chassis_upgrade_commit_resume(ctx):
    try:
        check_slots_upgrade_status(COMMIT_PAUSE)
        invoke_slots_upgrade_operation(ctx, slot_upgrade_commit_resume)
        ctx.invoke(cu_upgrade_commit_resume)
    except Exception as e:
        click.echo(e)

@chassis_upgrade.command('rollback')
@click.pass_context
def chassis_upgrade_rollback(ctx):
    try:
        invoke_slots_upgrade_operation(ctx, slot_upgrade_rollback) 
        ctx.invoke(cu_upgrade_rollback)
    except Exception as e:
        click.echo(e)

@click.group("upgrade")
@click.pass_context
def show_chassis_upgrade(ctx):
    pass

@show_chassis_upgrade.command('state')
@click.pass_context
def chassis_upgrade_state(ctx):
    try:
        show_chassis_upgrade_state()
    except Exception as e:
        click.echo(f'Query Failed, Wait for a moment and then try again. Error {e}')

def show_chassis_upgrade_state():
    chassis_upgrade_header = ['Module','Type', 'Status','CurrentVersion', 'UpgradeVersion']
    chassis_upgrade_info = []
    if not os.path.exists('/tmp/chassis_img/upgradecfg'):
        click.echo(f'Chassis upgrade state: IDLE')
        return
    
    with open(f"/tmp/chassis_img/upgradecfg", encoding='utf8') as fp:
        version_json = json.load(fp)
    
    for slot_idx in get_linecard_slot_range():
        card_type = get_card_type(slot_idx)
        software_version = get_slot_software_version(slot_idx)
        if get_card_is_present(slot_idx) and software_version != version_json[card_type]['ver']:
            state = get_slot_upgrade_state(slot_idx)
            chassis_upgrade_info.append([f"slot{slot_idx}", card_type, state, software_version, version_json[card_type]['ver']])
    
    cu_upgrade_version = version_json["sonic"]['ver'].replace("SONiC.", "")
    chassis_upgrade_info.append([f"cu-1", "", get_cu_upgrade_state(), get_cu_current_version(), cu_upgrade_version]) 
    chassis_upgrade_info.append([f"chassis", "", "", get_chassis_software_version(), version_json["chassis"]['ver']])    
    print(tabulate(chassis_upgrade_info, chassis_upgrade_header, tablefmt="simple"))
        
def check_slots_upgrade_status(expect_state):
    if not os.path.exists('/tmp/chassis_img/upgradecfg'):
        click.echo(f'Chassis upgrade state: IDLE')
        return
    
    with open(f"/tmp/chassis_img/upgradecfg", encoding='utf8') as fp:
        version_json = json.load(fp)
        
    for slot_idx in get_linecard_slot_range():
        card_type = get_card_type(slot_idx)
        software_version = get_slot_software_version(slot_idx)
        if get_card_is_present(slot_idx) and software_version != version_json[card_type]['ver']:
            state = get_slot_upgrade_state(slot_idx)
            if state != expect_state:
                raise Exception(f'Slot {slot_idx} upgrade state: {state} is NOT {expect_state}.')

def invoke_slots_download(ctx):
    with open(f"/tmp/chassis_img/upgradecfg", encoding='utf8') as fp:
        version_json = json.load(fp)
        
    for slot_idx in get_linecard_slot_range():
        card_type = get_card_type(slot_idx)
        software_version = get_slot_software_version(slot_idx)
        if get_card_is_present(slot_idx) and software_version != version_json[card_type]['ver']:
            bin_name = version_json[card_type]['bin']
            ctx.obj['slot_idx'] = int(slot_idx)
            ctx.invoke(slot_upgrade_download, file=f"/tmp/chassis_img/{bin_name}", uname='admin', password='YourPaSsWoRd') 

def get_cu_target_image():
    with open(f"/tmp/chassis_img/upgradecfg", encoding='utf8') as fp:
        version_json = json.load(fp)
    return version_json["sonic"]['bin']

def invoke_slots_upgrade_operation(ctx, slot_upgrade_operation_func):
    with open(f"/tmp/chassis_img/upgradecfg", encoding='utf8') as fp:
            version_json = json.load(fp)
        
    for slot_idx in get_linecard_slot_range():
        card_type = get_card_type(slot_idx)
        software_version = get_slot_software_version(slot_idx)
        if get_card_is_present(slot_idx) and software_version != version_json[card_type]['ver']:
            ctx.obj['slot_idx'] = int(slot_idx)
            ctx.invoke(slot_upgrade_operation_func)
        else:
            print(f"Slot {slot_idx} Upgrade Not Required") 

def report_upgrade_event(alarm_type_id):
    alarm_profile_dic = get_system_alarm_profile()
    alarm_info = alarm_profile_dic[alarm_type_id]
    time_created = int(time.time() * 1000000000)#ms
    alarm_id = f"CHASSIS-1#{alarm_type_id}"
    alarm_data = [
            ("id",f"{alarm_id}"),
            ("time-created",f"{time_created}"),
            ("resource","CHASSIS-1"),
            ("text",f"{alarm_info['Detail']}"),
            ("type-id",f"{alarm_type_id}"),
            ("severity",f"{alarm_info['Severity']}"),
            ("service-affect",f"{alarm_info['SA']}"),
        ]
    
    history_db = get_chassis_history_db() 
    set_table_fields(history_db, "HISEVENT", alarm_id, alarm_data)
    set_table_expire(history_db, "HISEVENT", alarm_id,EXPIRE_7_DAYS)
