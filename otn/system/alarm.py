import os
import click

from tabulate import tabulate
from otn.utils.db import *
from otn.utils.utils import *

################################### show #########################################################
@click.group()
@click.pass_context
def alarm(ctx):
    pass

@alarm.command()
def current():
    click.echo("SLOT:")
    for slot_id in get_linecard_slot_range():
        show_slot_alarm_current(slot_id)
    click.echo("CHASSIS:")
    show_chassis_alarm_current()

@alarm.command()
def history():
    click.echo("SLOT:")
    for slot_id in get_linecard_slot_range():
        show_slot_alarm_history(slot_id)
    click.echo("CHASSIS:")
    show_chassis_alarm_history()

@alarm.command()
def profile():
    alarm_profile_dic = get_system_alarm_profile()
    alarm_profile_header = ['Name','Severity','SA','Type', 'Detail']
    alarm_profile_info = []
    for alarm, profile in alarm_profile_dic.items():
        alarm_profile_info.append([alarm, profile['Severity'], profile['SA'], profile['Type'], profile['Detail']])
    click.echo(tabulate(alarm_profile_info, alarm_profile_header, tablefmt="simple"))
    click.echo("")

#################################### clear ############################################################
@click.command("clear-alarm")
@click.pass_context
def clear_alarm(ctx):
    pattern = "HISALARM:*"
    for slot_id in get_linecard_slot_range():
        db = get_history_db_by_slot(slot_id)
        message = clear_db_entity_alarm_history(db, pattern)
        click.echo(f"slot {slot_id} : {message}")
    db = get_chassis_history_db()
    message = clear_db_entity_alarm_history(db, pattern)
    click.echo(f"chassis : {message}")
