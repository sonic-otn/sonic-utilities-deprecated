import click

from otn.utils.utils import *

#################################### reboot ############################################################
@click.group()
@click.pass_context
def reboot(ctx):
    pass

@reboot.command("chassis")
@click.argument('reboot_type', type=click.Choice(["cold", "warm"]), required=True)
@click.pass_context
def reboot_chassis(ctx, reboot_type):
    try:
        run_command('sudo /usr/bin/save_history.sh', return_cmd=True)
        run_command('sudo sync')
        for slot_idx in get_linecard_slot_range():
            ctx.invoke(reboot_slot, slot_idx=slot_idx, reboot_type=reboot_type)
        ctx.invoke(reboot_cu, reboot_type=reboot_type)
        click.echo(f"chassis {reboot_type} rebooting...")
    except Exception as e:
        click.echo(e)
        
@reboot.command("cu")
@click.argument('reboot_type', type=click.Choice(["cold", "warm"]),required=True)
def reboot_cu(reboot_type):
    try:
        run_command('sudo /usr/bin/save_history.sh', return_cmd=True)
        run_command('sudo sync')
        db = get_chassis_state_db()
        db.publish("PERIPHERAL_REBOOT_CHANNEL", f"CU-1,{reboot_type.upper}")
        click.echo(f'CU {reboot_type} rebooting...')
    except Exception as e:
        click.echo(e)

@reboot.command("slot")
@click.argument('slot_idx',type=DynamicModuleIdxChoice('slot'), required=True)
@click.argument('reboot_type', type=click.Choice(["cold", "warm"]),required=True)
def reboot_slot(slot_idx,reboot_type):
    try:
        slot_id = int(slot_idx)
        if not get_card_is_present(slot_id):
            click.echo('Error: Card is Absent.')
            return

        if not slot_is_ready(slot_id) and reboot_type == 'warm':
            click.echo('Error: Card is Not Ready.') 
            return
    
        run_command('sudo sync')
        if reboot_type == "cold":
            db = get_chassis_state_db()
            db.publish("PERIPHERAL_REBOOT_CHANNEL", f"SLOT-{slot_id},{reboot_type.upper()}")
        else:
            run_OLSS_utils_set(slot_id, 'LINECARD', f'LINECARD-1-{slot_id}', 'reset', 'WARM')

        click.echo(f'Slot {slot_idx} {reboot_type} rebooting...')
    except Exception as e:
        click.echo(e)
