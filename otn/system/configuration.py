import click
import os
from otn.utils.classsftp import make_file_zip
from otn.utils.utils import *
from otn.system.sftp import sftp_get_file, sftp_put_file
from sonic_py_common import multi_asic
from swsssdk import ConfigDBConnector, SonicDBConfig
from swsscommon.swsscommon import SonicV2Connector

DEFAULT_CONFIG_DB_FILE = '/etc/sonic/config_db.json'
SONIC_CFGGEN_PATH = '/usr/local/bin/sonic-cfggen'
SONIC_DB_CLI="/usr/local/bin/sonic-db-cli"
INIT_CFG_FILE = '/etc/sonic/init_cfg.json'
NAMESPACE_PREFIX = 'asic'

@click.group('restore')
@click.pass_context
def restore(ctx):
    pass

@restore.command('remote-configuration')
@click.argument("ip_addr", metavar="<ip_addr>", required=True)
@click.argument('port',type=click.IntRange(0,65535),required=False,default=22)
@click.argument('tar_file_name',type=str,required=True)
@click.argument('uname',type=str,required=True)
@click.password_option(confirmation_prompt=False)
@click.pass_context
def restore_remote_configuration(ctx, ip_addr, port, tar_file_name, uname, password):
    '''config restore remote-configuration'''
    file_name = tar_file_name
    if tar_file_name.endswith('.tar'):
        file_name = tar_file_name[:-4]

    try:
        sftp_get_file(ip_addr, port, uname, password, tar_file_name, tar_file_name)

        cmd = f'sudo tar -zxf {tar_file_name} -C /tmp'
        if os.system(cmd) != 0:
            click.echo(f'Error: decompress {tar_file_name} Failed.')
            return

        if os.path.exists(f'/tmp/{file_name}'):
            os.system(f'sudo cp -rf /tmp/{file_name}/config_db* /etc/sonic/')
        if os.path.exists(f'/tmp/{file_name}/frr'):
            os.system(f'sudo cp -rf /tmp/{file_name}/frr /etc/sonic/')
        if os.path.exists(f'/tmp/{file_name}/passwd'):
            os.system(f'sudo cp -a /tmp/{file_name}/passwd /etc/passwd')
        if os.path.exists(f'/tmp/{file_name}/shadow'):
            os.system(f'sudo cp -a /tmp/{file_name}/shadow /etc/shadow')
        if os.path.exists(f'/tmp/{file_name}/group'):
            os.system(f'sudo cp -a /tmp/{file_name}/group /etc/group')
        if os.path.exists(f'/tmp/{file_name}/gshadow'):
            os.system(f'sudo cp -a /tmp/{file_name}/gshadow /etc/gshadow')
        if os.path.exists(f'/tmp/{file_name}/subgid'):
            os.system(f'sudo cp -a /tmp/{file_name}/subgid /etc/subgid')
        if os.path.exists(f'/tmp/{file_name}/subuid'):
            os.system(f'sudo cp -a /tmp/{file_name}/subuid /etc/subuid')

        run_system_command(f'sudo sync')
        run_system_command(f'sudo systemctl restart create-home-dirs.service')
        click.echo('Succeeded. Please reboot cu now to reload configuration!')
    except Exception as e:
        click.echo(e)
    finally:
        os.system(f'sudo rm -rf /tmp/{file_name}')
        os.system(f'sudo rm -rf {tar_file_name}')


@restore.command('factory-config')
@click.option('-y', '--yes', is_flag=True, callback=abort_if_false,
              expose_value=False, prompt='Current configuration will be replaced by factory configuration, continue?')
def restore_factory_config():
    '''restore factory configuration.'''
    if os.geteuid() != 0:
        exit("Root privileges required for this operation")
    try:
        run_system_command('config-setup factory')
        click.echo('Done. Please warm reboot chassis to reload factory configuration now.')
    except Exception as e:
        click.echo(e)

@click.group('backup')
@click.pass_context
def backup(ctx):
    '''upload saved-configuration'''
    ctx.obj = {}

@backup.command('saved-configuration')
@click.argument("ip_addr", metavar="<ip_addr>", required=True)
@click.argument('port',type=click.IntRange(0,65535),required=False,default=22)
@click.argument('file_name', type=str, required=True)
@click.argument('uname',type=str,required=True)
@click.password_option(confirmation_prompt=False)
@click.pass_context
def upload_saved_configuration(ctx, file_name, ip_addr, port, uname, password):
    '''upload saved configuration.'''
    if file_name.endswith('.tar'):
        file_name = file_name[:-4]
    try:
        if os.path.exists(file_name):
            os.system(f'sudo rm -rf {file_name}')
        os.system(f'sudo mkdir -p {file_name}')
        os.system(f'sudo cp -a /etc/passwd {file_name}')
        os.system(f'sudo cp -a /etc/shadow {file_name}')
        os.system(f'sudo cp -a /etc/group {file_name}')
        os.system(f'sudo cp -a /etc/gshadow {file_name}')
        os.system(f'sudo cp -a /etc/subgid {file_name}')
        os.system(f'sudo cp -a /etc/subuid {file_name}')
        os.system(f'sudo cp -a /etc/sonic/config_db*.json {file_name}')
        os.system(f'sudo cp -rf /etc/sonic/frr {file_name}')
        file_name_tar=f'{file_name}.tar'
        make_file_zip(file_name_tar,file_name)
        if os.path.isfile(file_name_tar):
            sftp_put_file(ip_addr, port, uname, password, file_name_tar, file_name_tar)
    except Exception as e:
        click.echo(e)
    finally:
        os.system(f'sudo rm -rf {file_name}')
        os.system(f'sudo rm -rf {file_name_tar}')

@click.command('current-configuration')
def current_configuration():
    cmd_all =""
    for id in get_linecard_slot_range():
        cmd = f'sonic-cfggen -n asic{id-1} -d -t /etc/sonic/current_linecard_configuration.j2'
        cmd_all +=  cmd + ";"
    else:
        cmd = "sonic-cfggen -d --print-data;"
        cmd_all += cmd
    cmd_all += 'docker exec -it bgp cat /etc/sonic/frr/bgpd.conf' + ';'
    cmd_all += 'docker exec -it bgp cat /etc/sonic/frr/ospfd.conf'
    run_system_command(cmd_all)

def get_namespaces():
    namespaces = ['host']
    if multi_asic.is_multi_asic():
        namespaces.extend(multi_asic.get_namespace_list())
    return namespaces

@click.command()
@click.option('-y', '--yes', is_flag=True, callback=abort_if_false,
              expose_value=False, prompt='Existing files will be overwritten, continue?')
@click.argument('filename', required=False)
@click.option('-n', '--namespace', help='Namespace name', type=click.Choice(get_namespaces()))
def save(filename, namespace):
    """Export current config DB to a file on disk.\n
       <filename> : Names of configuration file(s) to save, separated by comma with no spaces in between
    """
    num_asic = multi_asic.get_num_asics()
    cfg_files = []

    num_cfg_file = 1
    if multi_asic.is_multi_asic():
        num_cfg_file += num_asic

    # If the user give the filename[s], extract the file names.
    if filename is not None:
        cfg_files = filename.split(',')

        if len(cfg_files) != num_cfg_file and namespace is None:
            click.echo("Input {} config file(s) separated by comma for multiple files ".format(num_cfg_file))
            return

    if namespace is not None:
        if namespace == 'host':
            file = DEFAULT_CONFIG_DB_FILE
            if len(cfg_files) == 0:
                command = "{} -d --print-data > {}".format(SONIC_CFGGEN_PATH, file)
                run_command(command, display_cmd=True)
            else:
                command = "{} -d --print-data > {}".format(SONIC_CFGGEN_PATH, cfg_files[0])
                run_command(command, display_cmd=True)
        else:
            file = "/etc/sonic/config_db{}.json".format(namespace.split(NAMESPACE_PREFIX)[1])
            if len(cfg_files) == 0:
                command = "{} -n {} -d --print-data > {}".format(SONIC_CFGGEN_PATH, namespace, file)
                run_command(command, display_cmd=True)
            else:
                command = "{} -n {} -d --print-data > {}".format(SONIC_CFGGEN_PATH, namespace, cfg_files[0])
                run_command(command, display_cmd=True)
        return

    # In case of multi-asic mode we have additional config_db{NS}.json files for
    # various namespaces created per ASIC. {NS} is the namespace index.
    for inst in range(-1, num_cfg_file - 1):
        # inst = -1, refers to the linux host where there is no namespace.
        if inst == -1:
            namespace = None
        else:
            namespace = "{}{}".format(NAMESPACE_PREFIX, inst)

        # Get the file from user input, else take the default file /etc/sonic/config_db{NS_id}.json
        if cfg_files:
            file = cfg_files[inst + 1]
        else:
            if namespace is None:
                file = DEFAULT_CONFIG_DB_FILE
            else:
                file = "/etc/sonic/config_db{}.json".format(inst)

        if namespace is None:
            command = "{} -d --print-data > {}".format(SONIC_CFGGEN_PATH, file)
        else:
            command = "{} -n {} -d --print-data > {}".format(SONIC_CFGGEN_PATH, namespace, file)

        log.log_info("'save' executing...")
        run_command(command, display_cmd=True)

def _stop_services():
    try:
        subprocess.check_call("sudo monit status", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        click.echo("Disabling container monitoring ...")
        run_command("sudo monit unmonitor container_checker")
    except subprocess.CalledProcessError as err:
        pass

    click.echo("Stopping SONiC target ...")
    run_command("sudo systemctl stop sonic.target")


def _get_sonic_services():
    out = run_command("systemctl list-dependencies --plain sonic.target | sed '1d'", return_cmd=True)
    return [unit.strip() for unit in out.splitlines()]


def _reset_failed_services():
    for service in _get_sonic_services():
        click.echo("Resetting failed status on {}".format(service))
        run_command("systemctl reset-failed {}".format(service))

def _restart_services():
    click.echo("Restarting SONiC target ...")
    run_command("sudo systemctl restart sonic.target")

    # Reload Monit configuration to pick up new hostname in case it changed
    click.echo("Reloading Monit configuration ...")
    run_command("sudo monit unmonitor all")

    try:
        subprocess.check_call("sudo monit status", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        click.echo("Enabling container monitoring ...")
        run_command("sudo monit monitor container_checker")
    except subprocess.CalledProcessError as err:
        pass

@click.command()
@click.option('-y', '--yes', is_flag=True)
@click.argument('filename', required=False)
def load(filename, yes):
    """Import a previous saved config DB dump file.
       <filename> : Names of configuration file(s) to load, separated by comma with no spaces in between
    """
    if filename is None:
        message = 'Load config from the default config file(s) ?'
    else:
        message = 'Load config from the file(s) {} ?'.format(filename)

    if not yes:
        click.confirm(message, abort=True)

    num_asic = multi_asic.get_num_asics()
    cfg_files = []

    num_cfg_file = 1
    if multi_asic.is_multi_asic():
        num_cfg_file += num_asic

    # If the user give the filename[s], extract the file names.
    if filename is not None:
        cfg_files = filename.split(',')

        if len(cfg_files) != num_cfg_file:
            click.echo("Input {} config file(s) separated by comma for multiple files ".format(num_cfg_file))
            return

    # In case of multi-asic mode we have additional config_db{NS}.json files for
    # various namespaces created per ASIC. {NS} is the namespace index.
    for inst in range(-1, num_cfg_file - 1):
        # inst = -1, refers to the linux host where there is no namespace.
        if inst == -1:
            namespace = None
        else:
            namespace = "{}{}".format(NAMESPACE_PREFIX, inst)

        # Get the file from user input, else take the default file /etc/sonic/config_db{NS_id}.json
        if cfg_files:
            file = cfg_files[inst + 1]
        else:
            if namespace is None:
                file = DEFAULT_CONFIG_DB_FILE
            else:
                file = "/etc/sonic/config_db{}.json".format(inst)

        # if any of the config files in linux host OR namespace is not present, return
        if not os.path.exists(file):
            click.echo("The config_db file {} doesn't exist".format(file))
            return

        if namespace is None:
            command = "{} -j {} --write-to-db".format(SONIC_CFGGEN_PATH, file)
        else:
            command = "{} -n {} -j {} --write-to-db".format(SONIC_CFGGEN_PATH, namespace, file)

        log.log_info("'load' executing...")
        run_command(command, display_cmd=True)


@click.command()
@click.option('-y', '--yes', is_flag=True)
@click.option('-l', '--load-sysinfo', is_flag=True, help='load system default information (mac, portmap etc) first.')
@click.option('-n', '--no_service_restart', default=False, is_flag=True, help='Do not restart docker services')
@click.option('-d', '--disable_arp_cache', default=False, is_flag=True,
              help='Do not cache ARP table before reloading (applies to dual ToR systems only)')
@click.argument('filename', required=False)
def reload(filename, yes, load_sysinfo, no_service_restart, disable_arp_cache):
    """Clear current configuration and import a previous saved config DB dump file.
       <filename> : Names of configuration file(s) to load, separated by comma with no spaces in between
    """
    if filename is None:
        message = 'Clear current config and reload config from the default config file(s) ?'
    else:
        message = 'Clear current config and reload config from the file(s) {} ?'.format(filename)

    if not yes:
        click.confirm(message, abort=True)

    log.log_info("'reload' executing...")

    num_asic = multi_asic.get_num_asics()
    cfg_files = []

    num_cfg_file = 1
    if multi_asic.is_multi_asic():
        num_cfg_file += num_asic

    # If the user give the filename[s], extract the file names.
    if filename is not None:
        cfg_files = filename.split(',')

        if len(cfg_files) != num_cfg_file:
            click.echo("Input {} config file(s) separated by comma for multiple files ".format(num_cfg_file))
            return

    if load_sysinfo:
        command = "{} -j {} -v DEVICE_METADATA.localhost.hwsku".format(SONIC_CFGGEN_PATH, filename)
        proc = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE)
        cfg_hwsku, err = proc.communicate()
        if err:
            click.echo("Could not get the HWSKU from config file, exiting")
            sys.exit(1)
        else:
            cfg_hwsku = cfg_hwsku.strip()

    # Stop services before config push
    if not no_service_restart:
        log.log_info("'reload' stopping services...")
        _stop_services()

    # In Single ASIC platforms we have single DB service. In multi-ASIC platforms we have a global DB
    # service running in the host + DB services running in each ASIC namespace created per ASIC.
    # In the below logic, we get all namespaces in this platform and add an empty namespace ''
    # denoting the current namespace which we are in ( the linux host )
    for inst in range(-1, num_cfg_file - 1):
        # Get the namespace name, for linux host it is None
        if inst == -1:
            namespace = None
        else:
            namespace = "{}{}".format(NAMESPACE_PREFIX, inst)

        if inst != -1:
            command = "{} -n {} APPL_DB FLUSHDB".format(SONIC_DB_CLI, namespace)
            run_command(command, display_cmd=True)
            command = "{} -n {} ASIC_DB FLUSHDB".format(SONIC_DB_CLI, namespace)
            run_command(command, display_cmd=True)
            command = "{} -n {} COUNTERS_DB FLUSHDB".format(SONIC_DB_CLI, namespace)
            run_command(command, display_cmd=True)
            command = "{} -n {} FLEX_COUNTER_DB FLUSHDB".format(SONIC_DB_CLI, namespace)
            run_command(command, display_cmd=True)
            command = "{} -n {} STATE_DB FLUSHDB".format(SONIC_DB_CLI, namespace)
            run_command(command, display_cmd=True)

        # Get the file from user input, else take the default file /etc/sonic/config_db{NS_id}.json
        if cfg_files:
            file = cfg_files[inst + 1]
        else:
            if namespace is None:
                file = DEFAULT_CONFIG_DB_FILE
            else:
                file = "/etc/sonic/config_db{}.json".format(inst)

        # Check the file exists before proceeding.
        if not os.path.exists(file):
            click.echo("The config_db file {} doesn't exist".format(file))
            continue

        if namespace is None:
            config_db = ConfigDBConnector()
        else:
            print("call configDBConnector")
            config_db = ConfigDBConnector(use_unix_socket_path=True, namespace=namespace)

        config_db.connect()
        client = config_db.get_redis_client(config_db.CONFIG_DB)
        client.flushdb()
        if load_sysinfo:
            if namespace is None:
                command = "{} -H -k {} --write-to-db".format(SONIC_CFGGEN_PATH, cfg_hwsku)
            else:
                command = "{} -H -k {} -n {} --write-to-db".format(SONIC_CFGGEN_PATH, cfg_hwsku, namespace)
            run_command(command, display_cmd=True)

        # For the database service running in linux host we use the file user gives as input
        # or by default DEFAULT_CONFIG_DB_FILE. In the case of database service running in namespace,
        # the default config_db<namespaceID>.json format is used.
        if namespace is None:
            if os.path.isfile(INIT_CFG_FILE):
                command = "{} -j {} -j {} --write-to-db".format(SONIC_CFGGEN_PATH, INIT_CFG_FILE, file)
            else:
                command = "{} -j {} --write-to-db".format(SONIC_CFGGEN_PATH, file)
        else:
            if os.path.isfile(INIT_CFG_FILE):
                command = "{} -j {} -j {} -n {} --write-to-db".format(SONIC_CFGGEN_PATH, INIT_CFG_FILE, file, namespace)
            else:
                command = "{} -j {} -n {} --write-to-db".format(SONIC_CFGGEN_PATH, file, namespace)

        run_command(command, display_cmd=True)
        client.set(config_db.INIT_INDICATOR, 1)

    # We first run "systemctl reset-failed" to remove the "failed"
    # status from all services before we attempt to restart them
    if not no_service_restart:
        _reset_failed_services()
        log.log_info("'reload' restarting services...")
        _restart_services()

