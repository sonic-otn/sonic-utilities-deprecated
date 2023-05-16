import click

from swsssdk import ConfigDBConnector, SonicDBConfig
from swsscommon.swsscommon import SonicV2Connector

from otn.fan import fan
from otn.psu import psu
from otn.slot import slot
from otn.chassis import chassis
from otn.system import system_config
from otn.system import configuration
from otn.system import log
from otn.system import reboot
from otn.system import snmptrap
from otn.system import ntp
from otn.system import sftp
from otn.system import console
from otn.chassis import chassis
from otn.system import aaa
from otn.system import ip
from otn.system import syslog
from otn.utils.utils import load_chassis_capability

def add_otn_config_commands(config):
    config.add_command(fan.cfg_fan)
    config.add_command(psu.cfg_psu)
    config.add_command(chassis.cfg_chassis)
    config.add_command(slot.cfg_slot)
    config.add_command(slot.switch)
    config.add_command(slot.console_cfg)
    config.add_command(reboot.reboot)
    config.add_command(configuration.backup)
    config.add_command(configuration.restore)
    config.add_command(configuration.save)
    config.add_command(configuration.load)
    config.add_command(configuration.reload)
    config.add_command(log.export_log)
    config.add_command(sftp.sftpget)
    config.add_command(sftp.sftpput)
    config.add_command(snmptrap.snmptrap_cfg)
    config.add_command(ntp.ntp_cfg)
    config.add_command(console.console_cfg)
    config.add_command(ip.interface_cfg)
    config.add_command(aaa.aaa_cfg)
    config.add_command(aaa.tacacs_cfg)
    config.add_command(syslog.syslog_cfg)
    
    config.add_command(system_config.system)
    config.add_command(system_config.set_systime)
    config.add_command(system_config.timezone)
    config.add_command(system_config.sshd_alive_timeout)

@click.group()
@click.pass_context
def config(ctx):

    # Load the global config file database_global.json once.
    SonicDBConfig.load_sonic_global_db_config()

    ctx.obj = {}
    load_chassis_capability(ctx)

add_otn_config_commands(config)

if __name__ == '__main__':
    config()
