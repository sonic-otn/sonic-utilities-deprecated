import click
import subprocess

from otn.utils.utils import get_chassis_software_version, get_chassis_serial_number
from sonic_py_common import device_info
import otn_pmon.public as pmon_public


enum_reboot_type = {
    0: 'Cold boot/Power Cycle',
    1: 'Cold boot',
    2: 'Normal warm boot',
    3: 'Abnormal warm boot',
    4: 'Watchdog Reset',
    5: 'Reset Button',
}

@click.command()
def version():
    """Show version information"""
    upgrade_version = get_chassis_software_version()
    version_info = device_info.get_sonic_version_info()

    platform = device_info.get_platform()
    hwsku = device_info.get_hwsku()
    asic_type = version_info['asic_type']
    serial_number = get_chassis_serial_number()

    sys_ver = pmon_public.get_system_version()
    product_name = pmon_public.get_product_name()
    try:
        last_reboot = enum_reboot_type[pmon_public.get_reboot_type()]
    except:
        last_reboot = ''
    sys_uptime_cmd = "uptime"
    sys_uptime = subprocess.Popen(sys_uptime_cmd, shell=True, text=True, stdout=subprocess.PIPE)

    click.echo("\nSONiC Software Version: SONiC.{}".format(version_info['build_version']))
    click.echo("Distribution: Debian {}".format(version_info['debian_version']))
    click.echo("Kernel: {}".format(version_info['kernel_version']))
    click.echo("Build commit: {}".format(version_info['commit_id']))
    click.echo("Build date: {}".format(version_info['build_date']))
    click.echo("Build number: {}".format(version_info['build_number']))
    click.echo("Built by: {}".format(version_info['built_by']))
    click.echo("LAI Version: {}".format(version_info['lai_version']))
    click.echo("Chassis SoftwareVersion: {}".format(upgrade_version))
    click.echo("\nPlatform: {}".format(platform))
    click.echo("HwSKU: {}".format(hwsku))
    click.echo("Vendor: {}".format(asic_type))
    click.echo("Serial Number: {}".format(serial_number))
    click.echo("Product Name: {}".format(product_name))
    click.echo("PCB Version: {}".format(sys_ver.pcb))
    click.echo("BOM Version: {}".format(sys_ver.bom))
    click.echo("DevMgr Version: {}".format(sys_ver.devmgr))
    click.echo("UCD90120 Version: {}".format(sys_ver.ucd90120))
    click.echo("LastReboot: {}".format(last_reboot))
    click.echo("Uptime: {}".format(sys_uptime.stdout.read().strip()))
    click.echo("\nDocker images:")
    cmd = 'sudo docker images --format "table {{.Repository}}\\t{{.Tag}}\\t{{.ID}}\\t{{.Size}}"'
    p = subprocess.Popen(cmd, shell=True, text=True, stdout=subprocess.PIPE)
    click.echo(p.stdout.read())
