import click
import os
import time
import socket
import threading

from otn.utils.classsftp import make_file_zip, FTP_OPS
from otn.utils.utils import *
from otn.system.sftp import sftpput

@click.command('export-log')
@click.argument("ip_addr", metavar="<ip_addr>", required=True)
@click.argument('port',type=click.IntRange(0,65535),required=True,default=22)
@click.argument('remote_file',type=str,required=True)
@click.argument('uname',type=str,required=True)
@click.password_option(confirmation_prompt=False)
@click.pass_context
def export_log(ctx, ip_addr, port, remote_file, uname, password):
    if remote_file.endswith('.tar'):
        remote_file = remote_file[:-4]
    
    if not remote_file:
        zip_time = datetime.datetime.strftime(datetime.datetime.strptime(time.ctime(),'%a %b %d %H:%M:%S %Y'),'%Y-%m-%dT%H_%M_%S')
        remote_file = socket.gethostname() + f'_All_logs_{zip_time}'

    local_file_tar=f'/tmp/{remote_file}.tar'
    remote_file_tar = f'{remote_file}.tar'
        
    try: 
        log_dir = '/tmp/logs'
        get_cu_slots_log(log_dir)
        make_file_zip(local_file_tar, log_dir)
        ctx.invoke(sftpput, local_file=local_file_tar, remote_file=remote_file_tar, ip_addr=ip_addr, port=port, uname=uname, password=password)
    except Exception as e:
        click.echo(e)
    finally:
        os.system(f'sudo rm -rf {local_file_tar}')
        os.system(f'sudo rm -rf /tmp/logs')
        
def get_slot_log(slot_idx, log_file):
    if not slot_is_ready(slot_idx):
        click.echo(f'slot {slot_idx} status is not ready, skipping') 
        return
    if get_card_type(slot_idx) not in OBX1100E_LINECARDS:
        click.echo(f'slot {slot_idx} not support logs, skipping')
        return
    
    click.echo(f'Collecting slot {slot_idx} logs...') 
    run_OLSS_utils_set(slot_idx, 'LINECARD', f'LINECARD-1-{slot_idx}', 'collect-linecard-log', 'true')
    get_remote_slot_log(slot_idx, log_file)

def get_remote_slot_log(slot_idx, log_file, timeout=600):
    is_exist_path = '/mnt/flash/test_log'
    ftp = FTP_OPS(ftp_ip=LINECARD_IP_PREFIX + f'{slot_idx}',ftp_port=21,ftp_user='admin',ftp_pwd='YourPaSsWoRd')
    times = 1
    while True:
        if ftp.get_file_exist(is_exist_path,is_print=False):
            ftp.download_file(f'/mnt/flash/slot{slot_idx}Log.tar.gz',log_file)
            break
        if times >= timeout:
            raise Exception('Error: TimeOut. Not found file.')
        times += 1
        time.sleep(1)

def get_cu_slots_log(log_dir):        
    threads = []
    try:
        slots_log_folder = f'{log_dir}/board-log'
        if not os.path.exists(slots_log_folder):
            os.system(f'sudo mkdir -p {slots_log_folder}')
            
        for slot_idx in get_linecard_slot_range():
            slot_log_file = slots_log_folder +'/' + f'slot{slot_idx}Log.tar.gz'
            t = threading.Thread(target=get_slot_log, args=[slot_idx, slot_log_file])
            threads.append(t)
            t.start()
        
        cu_log_dir = f'{log_dir}/cu-log'
        t = threading.Thread(target=get_cu_log, args=[cu_log_dir])
        threads.append(t)
        t.start()
              
        for t in threads:
            t.join()
    except Exception as e:
        raise Exception(f'Error: Get slots log failed. {e}')

def get_cu_log(cu_log_folder):
    click.echo(f'Collecting CU logs...') 
    try:
        if not os.path.exists(cu_log_folder):
            os.system(f'sudo mkdir -p {cu_log_folder}')
            
        slot_log_file = cu_log_folder +'/' + f'CU_Log.tar'
        make_file_zip(slot_log_file, '/var/log')
    except Exception as e:
        raise Exception('Error: Get CU log failed.')