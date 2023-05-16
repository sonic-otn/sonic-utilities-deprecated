import os
import show.main as show
import config.main as config
from otn.utils.db import *
from click.testing import CliRunner


def cli_output_map_parser(output, headLineNum, footLineNum):
    data = output.split('\n')[headLineNum:footLineNum]
    result = {}
    for line in data:
        vaules=line.strip().split(": ")
        if len(vaules) == 2:
            result[vaules[0].strip()]= vaules[1].strip()
    return result

def load_slots_mock_data():
    test_path = os.path.dirname(__file__)
    init_db(0, DB_STATE_IDX, f'{test_path}/data/host/state_db.json')
    init_db(0, DB_CONFIG_IDX, f'{test_path}/data/host/config_db.json')
    init_db(0, DB_COUNTER_IDX, f'{test_path}/data/host/counter_db.json')
    init_db(0, DB_HISTORY_IDX, f'{test_path}/data/host/history_db.json')
    
    init_db(1, DB_STATE_IDX, f'{test_path}/data/asic0/state_db.json')
    init_db(1, DB_CONFIG_IDX, f'{test_path}/data/asic0/config_db.json')
    init_db(1, DB_COUNTER_IDX, f'{test_path}/data/asic0/counter_db.json')
    init_db(1, DB_HISTORY_IDX, f'{test_path}/data/asic0/history_db.json')
    
    init_db(2, DB_STATE_IDX, f'{test_path}/data/asic1/state_db.json')
    init_db(2, DB_CONFIG_IDX, f'{test_path}/data/asic1/config_db.json')
    init_db(2, DB_COUNTER_IDX, f'{test_path}/data/asic1/counter_db.json')
    init_db(2, DB_HISTORY_IDX, f'{test_path}/data/asic1/history_db.json')
    
    init_db(3, DB_STATE_IDX, f'{test_path}/data/asic2/state_db.json')
    init_db(3, DB_CONFIG_IDX, f'{test_path}/data/asic2/config_db.json')
    init_db(3, DB_COUNTER_IDX, f'{test_path}/data/asic2/counter_db.json')
    init_db(3, DB_HISTORY_IDX, f'{test_path}/data/asic2/history_db.json')
    
    init_db(4, DB_STATE_IDX, f'{test_path}/data/asic3/state_db.json')
    init_db(4, DB_CONFIG_IDX, f'{test_path}/data/asic3/config_db.json')
    init_db(4, DB_COUNTER_IDX, f'{test_path}/data/asic3/counter_db.json')
    init_db(4, DB_HISTORY_IDX, f'{test_path}/data/asic3/history_db.json')

def clean_slots_mock_data():
    uninit_db(0, DB_STATE_IDX)
    uninit_db(0, DB_CONFIG_IDX)
    uninit_db(0, DB_COUNTER_IDX)
    uninit_db(0, DB_HISTORY_IDX)
    
    uninit_db(1, DB_STATE_IDX)
    uninit_db(1, DB_CONFIG_IDX)
    uninit_db(1, DB_COUNTER_IDX)
    uninit_db(1, DB_HISTORY_IDX)

    uninit_db(2, DB_STATE_IDX)
    uninit_db(2, DB_CONFIG_IDX)
    uninit_db(2, DB_COUNTER_IDX)
    uninit_db(2, DB_HISTORY_IDX)
    
    uninit_db(3, DB_STATE_IDX)
    uninit_db(3, DB_CONFIG_IDX)
    uninit_db(3, DB_COUNTER_IDX)
    uninit_db(3, DB_HISTORY_IDX)
    
    uninit_db(4, DB_STATE_IDX)
    uninit_db(4, DB_CONFIG_IDX)
    uninit_db(4, DB_COUNTER_IDX)
    uninit_db(4, DB_HISTORY_IDX)
    
class TestChassis(object):
    @classmethod
    def setup_class(cls):
        os.environ['UTILITIES_UNIT_TESTING'] = "1"
        load_slots_mock_data()
        print("SETUP")
        
    def test_show_chassis_info(self):
        runner = CliRunner()
        result = runner.invoke(show.cli, ['chassis', '1', 'info'])
        assert result.exit_code == 0
        print(result.output)
        result_dict = cli_output_map_parser(result.output, 0, -1)
        assert result_dict["Part no"]=='1141TAC000'
        assert result_dict["Serial no"]=='AC0408163008'
        assert result_dict["Hardware ver"]=='1.11'
        assert result_dict["Software ver"]=='V100R001C002B097'
        assert result_dict["Mfg name"]=='alibaba'
        assert result_dict["Mfg date"]=='2022-08-15'
        assert result_dict["Temperature(C)"]=='25.0'
        assert result_dict["Inlet(C)"]=='27.5'
        assert result_dict["Outlet(C)"]=='29.0'

    def test_show_chassis_config(self):
        runner = CliRunner()
        result = runner.invoke(show.cli, ['chassis', '1', 'config'])
        assert result.exit_code == 0
        # print(result.output)
        result_dict = cli_output_map_parser(result.output, 0, -1)
        assert result_dict["Temp Hi-Alarm(C)"]=='70.0'
        assert result_dict["Temp Hi-Warning(C)"]=='65.0'
        assert result_dict["Temp Low-Alarm(C)"]=='10.0'
        assert result_dict["Temp Low-Warning(C)"]=='15.0'

    def test_show_chassis_slots(self):
        runner = CliRunner()
        result = runner.invoke(show.cli, ['chassis', '1', 'slots'])
        assert result.exit_code == 0
        lines = result.output.split('\n')[2:]
        assert lines[0]=='     1  P230C   Ready     P230CAC000  AC0405157001  1.0         Sonic-P230C-B019      28.00'
        assert lines[1]=='     2  E120C   Ready     E120CAC000  AC04B2167002  1.2         Sonic-E1X0C-B019      19.20'
        assert lines[2]=='     3  E100C   Ready     E100CAC000  AC04B0168004  1.2         Sonic-E1X0C-B019      19.60'
        assert lines[3]=='     4  E100C   Ready     E100CAC000  AC04B0167002  1.2         Sonic-E1X0C-B019      19.50'
        assert lines[4]=='     5  PSU     Mismatch  CRPS1300D   2K120053149   NA          N/A                   23.00'
        assert lines[5]=='     6  PSU     Mismatch  CRPS1300D   2K120053148   NA          N/A                   54.00'
        assert lines[6]=='     7  FAN     Ready     FANAC000    AC042315801B  2.0         N/A                   25.00'
        assert lines[7]=='     8  FAN     Ready     FANAC000    AC042315801A  2.0         N/A                   26.00'
        assert lines[8]=='     9  FAN     Ready     FANAC000    AC042315801C  2.0         N/A                   26.00'
        assert lines[9]=='    10  FAN     Ready     FANAC000    AC042315801D  2.0         N/A                   29.00'
        assert lines[10]== '    11  FAN     Ready     FANAC000    AC042315801E  2.0         N/A                   29.00'
    
    def test_show_chassis_alarm_current(self):
        runner = CliRunner()
        result = runner.invoke(show.cli, ['chassis', '1', 'alarm', 'current'])
        assert result.exit_code == 0
        # print(result.output)
        assert 'System Current Alarm Total num: 2' in result.output

    def test_show_chassis_alarm_history(self):
        runner = CliRunner()
        result = runner.invoke(show.cli, ['chassis', '1', 'alarm', 'history'])
        assert result.exit_code == 0
        # print(result.output)
        assert 'System History Alarm History Alarm Total num: 1' in result.output

    def test_show_chassis_pm_15_current(self):
        runner = CliRunner()
        result = runner.invoke(show.cli, ['chassis', '1', 'pm', '15', 'current'])
        assert result.exit_code == 0
        # print(result.output)
        lines = result.output.split('\n')[5:]
        # print(lines)
        assert lines[0]=='Temperature(C)  25         24.8   24.5   25     2023-03-30 11:30:07  2023-03-30 11:30:12  incomplete'
        assert lines[1]=='Inlet(C)        27.5       27.5   27.5   27.5   2023-03-30 11:30:07  2023-03-30 11:30:07  incomplete'
        assert lines[2]=='Outlet(C)       29         29.12  29     30     2023-03-30 11:30:07  2023-03-30 11:31:16  incomplete'
    
    def test_show_chassis_pm_24_current(self):
        runner = CliRunner()
        result = runner.invoke(show.cli, ['chassis', '1', 'pm', '24', 'current'])
        assert result.exit_code == 0
        # print(result.output)
        lines = result.output.split('\n')[5:]
        # print(lines)
        assert lines[0]=='Temperature(C)  25         25     24.5   25.5   2023-03-30 02:26:58  2023-03-30 00:28:18  incomplete'
        assert lines[1]=='Inlet(C)        27.5       27.81  27.5   28.5   2023-03-30 01:53:31  2023-03-30 00:56:59  incomplete'
        assert lines[2]=='Outlet(C)       29         29.64  29     30     2023-03-30 00:00:28  2023-03-30 00:00:07  incomplete'
                                   
    @classmethod
    def teardown_class(cls):
        os.environ['UTILITIES_UNIT_TESTING'] = "0"
        clean_slots_mock_data()
        print("TEARDOWN")