import click
import os

from otn_pmon.public import switch_slot_uart

from otn.utils.utils import run_command, get_linecard_slot_range
from otn.utils.config_utils import set_chassis_configuration_save
from otn.slot.slot import slot_baudrate_cfg

@click.group()
@click.pass_context
def console(ctx):
    pass

@console.command()
@click.pass_context
def baudrate(ctx):
    cmd = '''sudo stty -F /dev/ttyS0 | grep "speed" | awk "{{print $2}}"'''
    try:
        info = run_command(cmd,return_cmd=True)
        click.echo(f'Current baudrate is {info.split(" ")[1]}')
    except Exception as e:
        click.echo(e)

@click.group("console")
@click.pass_context
def console_cfg(ctx):
    pass
        
@console_cfg.command("baudrate")
@click.argument('baudrate_value',type=click.Choice(['9600','19200','38400','57600','115200']),required=True)
@click.pass_context
def baudrate_cfg(ctx, baudrate_value):
    try:
        for slot_id in get_linecard_slot_range():
            ctx.obj['slot_idx'] = int(slot_id)
            ctx.invoke(slot_baudrate_cfg, baudrate_value=baudrate_value)
        config_cu_console_baudrate(baudrate_value)
        set_chassis_configuration_save("DEVICE_METADATA", "localhost", "baudrate", baudrate_value)      
    except Exception as e:
        click.echo(e)

@console_cfg.command("switch")
@click.argument('console_id',type=click.IntRange(0,4),required=True)
def switch(console_id):
    status_num = switch_slot_uart(console_id)
    if console_id == 0:
        cmd="sudo stty -F /dev/ttyS0 cread ; sudo systemctl restart serial-getty@ttyS0.service"
    else:
        cmd = "sudo stty -F /dev/ttyS0 -cread"
    os.system(cmd)

    if status_num == 0:
        click.echo('Succeeded')
    else:
        click.echo('Failed')
        
def config_cu_console_baudrate(baudrate_value):
    cmd_1 = "sudo systemctl stop serial-getty@ttyS0.service"
    cmd_2 = f'sudo stty -F /dev/ttyS0 ispeed {baudrate_value} ospeed {baudrate_value} cs8'
    cmd_3 = f"sudo sed -i 's/115200\|19200\|38400\|57600\|9600/{baudrate_value}/g' /lib/systemd/system/serial-getty@.service"
    cmd_4 = "sudo systemctl daemon-reload"
    cmd_5 = "sudo systemctl restart serial-getty@ttyS0.service"
    run_command(cmd_1)
    run_command(cmd_2)
    run_command(cmd_3)
    run_command(cmd_4)
    run_command(cmd_5)
