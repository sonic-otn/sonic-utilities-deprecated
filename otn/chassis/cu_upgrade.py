import click

from sonic_py_common import device_info
from otn.utils.utils import *
from otn.slot.slot_upgrade import *
from otn.system.reboot import reboot_cu
from otn.system.sftp import sftp_get_file

#####################################upgrade########################################################
@click.group("cu")
@click.pass_context
def cu_config(ctx):
    pass

@cu_config.group("upgrade")
@click.pass_context
def cu_upgrade(ctx):
    pass

@cu_upgrade.command('auto')
@click.argument("ip_addr", metavar="<ip_addr>", required=True)
@click.argument('port',type=click.IntRange(0,65535),required=False,default=22)
@click.argument('file',type=str,required=True)
@click.argument('uname',type=str,required=True)
@click.password_option(confirmation_prompt=False)
@click.pass_context
def cu_upgrade_auto(ctx, ip_addr, port, file, uname, password):
    try:
        ctx.invoke(cu_upgrade_download, ip_addr=ip_addr, port=port, file=file, uname=uname, password=password)
        ctx.invoke(cu_upgrade_commit)
        ctx.invoke(cu_upgrade_reboot)
    except Exception as e:
        click.echo(e)

@cu_upgrade.command('download')
@click.argument("ip_addr", metavar="<ip_addr>", required=True)
@click.argument('port',type=click.IntRange(0,65535),required=False,default=22)
@click.argument('file',type=str,required=True)
@click.argument('uname',type=str,required=True)
@click.password_option(confirmation_prompt=False)
@click.pass_context
def cu_upgrade_download(ctx, ip_addr, port, file, uname, password):
    try:
        file_basename = os.path.basename(file)
        if not file_basename.endswith('.bin'):
            click.echo("Download file extension must be .bin")
            return

        if get_cu_upgrade_state() == DOWNLOADING:
            click.echo("Error, CU upgrade state is DOWNLOADING, exit.")
            return
        
        os.system(f'sudo mkdir -p /tmp/cu_img')
        update_cu_upgrade_state(DOWNLOADING)
        sftp_get_file(ip_addr, port, uname, password, '/tmp/cu_img/cu_img.bin', file)
        update_cu_upgrade_state(DOWNLOAD_FINISH)
    except Exception as e:
        click.echo(e)

@cu_upgrade.command("commit")
@click.pass_context
def cu_upgrade_commit(ctx):
    try:        
        cu_upgrade_commit_impl("/tmp/cu_img/cu_img.bin")
    except Exception as e:
        update_cu_upgrade_state(COMMIT_ERROR)
        click.echo(e)

@cu_upgrade.command("reboot")
@click.pass_context
def cu_upgrade_reboot(ctx):
    try:
        state = get_cu_upgrade_state()
        if state != COMMIT_FINISH:
            click.echo("CU upgrade state is not COMMIT_FINISH, exit.")
            return
        ctx.invoke(reboot_cu, reboot_type="warm") 
    except Exception as e:
        update_cu_upgrade_state(REBOOT_ERROR)
        click.echo(e)
    finally:
        os.system(f'sudo rm -rf /tmp/cu_img')

@cu_upgrade.command('commit-pause')
@click.pass_context
def cu_upgrade_commit_pause(ctx):
    click.echo("Trigger cu commit-pause Successed")

@cu_upgrade.command('commit-resume')
@click.pass_context
def cu_upgrade_commit_resume(ctx):
    click.echo("Trigger cu commit-resume Successed")

@cu_upgrade.command('rollback')
@click.pass_context
def cu_upgrade_rollback(ctx):
    try:
        sonic_ver = get_cu_current_version()
        os.system(f'sudo sonic-installer set-default SONiC-OS-{sonic_ver} >> /dev/null')
        update_cu_upgrade_state(IDLE)
        click.echo("Trigger cu Rollback Successed")
    except Exception as e:
        click.echo(e)

@click.group("cu")
@click.pass_context
def show_cu(ctx):
    pass

@show_cu.group("upgrade")
@click.pass_context
def show_cu_upgrade(ctx):
    pass

@show_cu_upgrade.command('state')
@click.pass_context
def cu_upgrade_state(ctx):
    try:
        click.echo(f"cu upgrade state: {get_cu_upgrade_state()}")
        os.system(f'sudo sonic-installer list')
    except Exception as e:
        click.echo(e)

def cu_upgrade_commit_impl(cu_image):
    state = get_cu_upgrade_state()
    if state != DOWNLOAD_FINISH:
        click.echo("Error, CU upgrade state is not DOWNLOAD_FINISH, exit.")
        return
    
    click.echo("Trigger cu Commit")
    update_cu_upgrade_state(COMMITING)
    os.system(f'sudo sonic-installer cleanup -y  >> /dev/null')
    os.system(f'sudo sonic-installer install {cu_image} -y  >> /dev/null')
    click.echo("Successed")
    update_cu_upgrade_state(COMMIT_FINISH)


def get_cu_current_version():
    version_info = device_info.get_sonic_version_info()
    return version_info['build_version']

def update_cu_upgrade_state(state):
    db = get_chassis_state_db()
    set_table_field(db, "CU", "CU-1", "upgrade-state", state)

def get_cu_upgrade_state():
    db = get_chassis_state_db()
    return get_db_table_field(db, "CU", "CU-1", "upgrade-state")