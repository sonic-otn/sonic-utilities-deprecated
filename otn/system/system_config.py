import click

from otn.utils.utils import *
from otn.utils.config_utils import set_chassis_configuration_save
from otn.utils.config_utils import set_slot_configuration_save

@click.group()
def system():
    pass

@system.command()
@click.argument('hname',type=str,required=True)
def hostname(hname):
    if not hname.strip()[0].isalpha():
        click.echo(f'Error: Invalid value for "HOSTNAME": {hname.strip()[0]} is invalid for the first char for hostname.')
        return
    for s in hname.strip():
        if s.isalpha() or s.isdigit() or s in ('-',):
            continue
        click.echo(f'Error: Invalid value for "HOSTNAME": {s} is invalid char for hostname.')
        return
    
    try:
        for slot_id in get_linecard_slot_range():
            if get_slot_card_type(slot_id) == 'P230C':
                set_slot_configuration_save(slot_id,'LINECARD',f'LINECARD-1-{slot_id}','hostname', hname.strip())
    
        _change_hostname(hname.strip())
        click.echo('Succeeded')
    except Exception as e:
        click.echo(e)

@system.command()
@click.argument('zone',type=str,required=True)
def timezone(zone):
    '''config system timezone <Asia/Shanghai>
     or UTC,UTC+8,UTC-10 +<1-12> -<1-12> or Etc/GMT ..
     Support all supported time zones
    '''
    table_name = 'DEVICE_METADATA'
    table_key = 'localhost'
    table_field = 'timezone'
    list_time_zone = get_time_zone()[1]
    if 'UTC' in zone:
        if zone == 'UTC':
            zone = '+0000'
        elif int(zone[4:]) in range(0,13) and zone[3] == '+' or int(zone[4:]) in range(0,13) and zone[3] == '-':
            zone = f'{zone[3]}{int(zone[4:]):02}00'
        else:
            click.echo('Error: timezone is not valid')
            return
        time_zone = get_time_zone(zone)[0]
        set_chassis_configuration_save(table_name, table_key, table_field, time_zone)
        click.echo('Succeeded')
    elif zone in list_time_zone:
        set_chassis_configuration_save(table_name, table_key, table_field, zone)
        click.echo('Succeeded')
    else:
        click.echo('Error: timezone is not avlid')


@click.command('systime')
@click.argument('dat',type=str,required=True)
@click.argument('day',type=str,required=False)
def set_systime(dat,day):
    '''config system time
       %Y-%m-%d %H:%M:%S or %Y-%m-%d or %H:%M:%S
    '''
    if not day:
        day = ''
    date_day = f'{dat} {day}'

    if not is_valid_time(dat,day):
        click.echo(f'Error: Invalid time of {date_day}. Valid time range is {SYSTIME_LOW} ~ {SYSTIME_HIGH}.')
    cmd = f'sudo date -s "{date_day}"'
    run_system_command(cmd)
    cmd2 = 'hwclock --systohc'
    run_system_command(cmd2)

@system.command('sshd-alive-timeout')
@click.argument('timeout',type=click.IntRange(30,1800),required=True)
def sshd_alive_timeout(timeout):
    table_name = 'DEVICE_METADATA'
    table_key = 'localhost'
    table_field = 'sshd-alive-timeout'
    set_chassis_configuration_save(table_name, table_key, table_field, str(timeout))
    click.echo('Succeeded')

def _change_hostname(hostname):
    current_hostname = os.uname()[1]
    if current_hostname != hostname:
        run_command('echo {} > /etc/hostname'.format(hostname), display_cmd=True)
        run_command('hostname -F /etc/hostname', display_cmd=True)
        run_command('sed -i "/\s{}$/d" /etc/hosts'.format(current_hostname), display_cmd=True)
        run_command('echo "127.0.0.1 {}" >> /etc/hosts'.format(hostname), display_cmd=True)
        set_chassis_configuration_save('DEVICE_METADATA', 'localhost', 'hostname', current_hostname)

