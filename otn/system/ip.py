import click
import netaddr
import netifaces
import ipaddress

from tabulate import tabulate
from natsort import natsorted
from otn.utils.utils import *
from sonic_py_common import device_info
from otn.utils.config_utils import set_chassis_configuration_save, delete_chassis_configuration_save

interface_map={ "eth1":"eth1", 
                "eth2":"eth0.1", 
                "osc1":"eth0.3",
                "osc2":"eth0.4",
                "osc3":"eth0.5",
                "osc4":"eth0.6"}

@click.group()
def ip():
    pass

@ip.command()
def interfaces():
    """Show interfaces IPv4 address"""
    header = ['Interface', 'IPv4 address/mask', 'Admin/Oper']
    data = []

    interfaces = natsorted(netifaces.interfaces())
    ETH_OSC_INTERFACE = {v:k for k,v in OSC_INTERFACE.items()}
    ETH_OSC_INTERFACE['eth0.1'] = 'eth2'

    for iface in interfaces:
        ipaddresses = netifaces.ifaddresses(iface)

        if netifaces.AF_INET in ipaddresses:
            ifaddresses = []
            for ipaddr in ipaddresses[netifaces.AF_INET]:
                local_ip = str(ipaddr['addr'])
                netmask = netaddr.IPAddress(ipaddr['netmask']).netmask_bits()
                ifaddresses.append(["", local_ip + "/" + str(netmask)])

            if len(ifaddresses) > 0:
                admin = get_if_admin_state(iface)
                if admin == "up":
                    oper = get_if_oper_state(iface)
                else:
                    oper = "down"
                
                iface = get_display_interface_name(iface)
                if iface is not None:
                    data.append([iface, ifaddresses[0][1], admin + "/" + oper])

    print(tabulate(data, header, tablefmt="simple", stralign='left', missingval=""))

@click.group("interface")
@click.pass_context
def interface_cfg(ctx):
    pass

@interface_cfg.group("ip")
@click.pass_context
def ip_cfg(ctx):
    pass

@ip_cfg.command()
@click.argument('interface_name', metavar='<interface_name>', required=True)
@click.argument("ip_addr", metavar="<ip_addr>", required=True)
@click.argument('gw', metavar='[default gateway IP address]', required=False)
@click.pass_context
def add(ctx, interface_name, ip_addr, gw):
    try:
        net = ipaddress.ip_network(ip_addr, strict=False)
        if '/' not in ip_addr:
            ip_addr = str(net)
            click.echo(f"{ip_addr} lack netmask!")
            return

        if interface_name == 'loopback':
            set_chassis_configuration_save("LOOPBACK_INTERFACE", f"Loopback0|{ip_addr}", "NULL", "NULL")
            device_info.update_loopbackrule()
        else:
            table_name = get_interface_db_table_name(interface_name)
            real_interface = get_real_interface_name(interface_name)
            if real_interface is None:
                click.echo(f"Error, invalid interface {interface_name}")
                return
            
            if not gw:
                set_chassis_configuration_save(table_name, f"{real_interface}|{ip_addr}", "NULL", "NULL")
            else:
                set_chassis_configuration_save(table_name, f"{real_interface}|{ip_addr}", "gwaddr", gw)
                
            cmd = "systemctl restart interfaces-config"
            run_command(cmd)  
        click.echo('Succeeded')
    except ValueError:
        click.echo("Error: 'ip_addr' is not valid.")


@ip_cfg.command()
@click.argument('interface_name', metavar='<interface_name>', required=True)
@click.argument("ip_addr", metavar="<ip_addr>", required=True)
@click.pass_context
def delete(ctx, interface_name, ip_addr):
    try:
        net = ipaddress.ip_network(ip_addr, strict=False)
        if '/' not in ip_addr:
            ip_addr = str(net)

        if interface_name == 'loopback':
            real_interface = "Loopback0"
            delete_chassis_configuration_save("LOOPBACK_INTERFACE", f"{real_interface}|{ip_addr}")
            device_info.update_loopbackrule()
        else:
            table_name = get_interface_db_table_name(interface_name)
            real_interface = get_real_interface_name(interface_name)
            if real_interface is None:
                click.echo(f"Error, invalid interface {interface_name}")
                return
            delete_chassis_configuration_save(table_name, f"{real_interface}|{ip_addr}")
         
        cmd = f"systemctl restart interfaces-config"
        run_command(cmd)  
        click.echo('Succeeded')
    except Exception as e:
        click.echo(f"Error: error {e}.")

def get_if_admin_state(iface):
    admin_file = "/sys/class/net/{0}/flags"

    try:
        state_file = open(admin_file.format(iface), "r")
    except IOError as e:
        print("Error: unable to open file: %s" % str(e))
        return "error"

    content = state_file.readline().rstrip()
    flags = int(content, 16)

    if flags & 0x1:
        return "up"
    else:
        return "down"
    
def get_if_oper_state(iface):
    oper_file = "/sys/class/net/{0}/carrier"

    try:
        state_file = open(oper_file.format(iface), "r")
    except IOError as e:
        print("Error: unable to open file: %s" % str(e))
        return "error"

    oper_state = state_file.readline().rstrip()
    if oper_state == "1":
        return "up"
    else:
        return "down"

def get_real_interface_name(interface):
    if interface in interface_map:
        return interface_map[interface]
    else:
        return None

def get_display_interface_name(interface):
    for k, v in interface_map.items(): 
        if v == interface:
            return k
    if interface == 'Loopback0':
        return 'loopback'
    return None

def get_interface_db_table_name(interface):
    if interface == "eth1":
        return "MGMT_INTERFACE"
    elif interface == "eth2":
        return "MGMT_INTERFACE2"
    elif "osc" in interface:
        return "OSC_INTERFACE"
    else:
        return None
