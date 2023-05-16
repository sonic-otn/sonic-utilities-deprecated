import click

from otn.slot import slot
from otn.chassis import chassis
from otn.fan import fan
from otn.psu import psu
from otn.system import alarm
from otn.system import ntp
from otn.system import configuration
from otn.system import snmptrap
from otn.system import telemetry
from otn.system import system_show
from otn.system import version
from otn.system import aaa
from otn.system import ip
from otn.system import syslog
from otn.system import console
from otn.utils.utils import load_chassis_capability

def add_otn_show_commands(show):
    show.add_command(chassis.chassis)
    show.add_command(slot.slot)
    show.add_command(chassis.chassis)
    show.add_command(fan.fan)
    show.add_command(psu.psu)
    show.add_command(alarm.alarm)
    show.add_command(ntp.ntp)
    show.add_command(snmptrap.snmptrap)
    show.add_command(telemetry.telemetry)
    show.add_command(version.version)
    show.add_command(aaa.aaa)
    show.add_command(aaa.tacacs)
    show.add_command(ip.ip)
    show.add_command(syslog.syslog)
    show.add_command(console.console)
    
    show.add_command(configuration.current_configuration)
    show.add_command(system_show.systime)
    show.add_command(system_show.netstat)
    show.add_command(system_show.process)
    show.add_command(system_show.route)
    show.add_command(system_show.system)
    show.add_command(system_show.tcp)
    show.add_command(system_show.top)
    show.add_command(system_show.ifconfig)
    show.add_command(system_show.users)
    show.add_command(system_show.log_file)


@click.group()
@click.pass_context
def show(ctx):
    ctx.obj = {}
    load_chassis_capability(ctx)

add_otn_show_commands(show)

if __name__ == '__main__':
    show()
