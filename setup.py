# https://github.com/ninjaaron/fast-entry_points
# workaround for slow 'pkg_resources' import
#
# NOTE: this only has effect on console_scripts and no speed-up for commands
# under scripts/. Consider stop using scripts and use console_scripts instead
#
# https://stackoverflow.com/questions/18787036/difference-between-entry-points-console-scripts-and-scripts-in-setup-py

from setuptools import setup

setup(
    name='sonic-utilities',
    version='1.2',
    description='Command-line utilities for SONiC OTN',
    license='Apache 2.0',
    author='SONiC OTN Team',
    url='https://github.com/zhengweitang-zwt/sonic-utilities',
    maintainer='Weitang Zheng',
    maintainer_email='zhengweitang.zwt@alibaba-inc.com',
    packages=[
        'sonic_installer',
        'sonic_installer.bootloader',
        'tests',
        'otn',
        'otn.chassis',
        'otn.fan',
        'otn.psu',
        'otn.slot',
        'otn.system',
        'otn.utils',
    ],
    package_data={
        'otn.utils': ['data/*.json'],
        'sonic_installer': ['aliases.ini'],
        'tests': ['*.json']
    },
    
    entry_points={
        'console_scripts': [
            'config = otn.config_main:config',
            'show = otn.show_main:show',
            'sonic-installer = sonic_installer.main:sonic_installer',
        ]
    },
    install_requires=[
        'click==7.0',
        'ipaddress==1.0.23',
        'm2crypto==0.31.0',
        'natsort==6.2.1',
        'netaddr==0.8.0',
        'netifaces==0.10.7',
        'pexpect==4.8.0',
        'cryptography==36.0.2',
        'paramiko==2.7.2',
        'sonic-platform-common',
        'sonic-py-common',
        'swsssdk>=2.0.1',
        'tabulate==0.8.2',
        'pytz==2022.1',
        'thrift==0.13.0',
    ],
    setup_requires= [
        'pytest-runner',
        'wheel'
    ],
    tests_require = [
        'pytest',
        'mockredispy>=2.9.3',
        'sonic-config-engine'
    ],
    keywords='sonic SONiC utilities command line cli CLI',
)
