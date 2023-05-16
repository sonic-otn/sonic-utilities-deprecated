import json
from .constants import *
import os
import otn

MAX_LINECARD_SLOT = 4
redis_instance = []
db_seperator = [None]*(DB_HISTORY_IDX+1)
db_seperator[DB_COUNTER_IDX] = ':'
db_seperator[DB_CONFIG_IDX] = '|'
db_seperator[DB_STATE_IDX] = '|'
db_seperator[DB_HISTORY_IDX] = ':'

class rdict(dict):
    def __init__(self, *args, **kwargs):
        self.update(dict(*args, **kwargs))

    #return NA if key not exist   
    def __getitem__(self, key):
        return dict.get(self, key, NA_VALUE)

for slot in range(0, MAX_LINECARD_SLOT+1):
    db_instance = []
    for db_idx in range(0, DB_HISTORY_IDX+1):
        db_table = rdict({})
        db_instance.append(db_table)
    redis_instance.append(db_instance)

def init_db(slot_id, db_id, filename):
    with open(filename) as f:
        js = json.load(f)
        redis_instance[slot_id][db_id] = rdict(js)
        redis_instance[slot_id][db_id]['seperator']=db_seperator[db_id]

def uninit_db(slot_id, db_id):
    redis_instance[slot_id][db_id].clear()
    
def connect_muti_db_common(slot_id, db_id):
    return redis_instance[slot_id][db_id]

def set_table_field(db,table_name,table_key,field,value):
    seperator = db['seperator']
    db[table_name+seperator+table_key][field]=str(value)

def set_table_fields(db,table_name,table_key, field_value_touple_list):
    for field_value in field_value_touple_list:
        field = field_value[0]
        value = field_value[1]
        db[table_name][table_key][field]=value

def set_table_expire(db,table_name,table_key, expire_time):
    pass

def del_table_field(db,table_name,table_key,field):
    db[table_name][table_key].pop(field, None)

def get_db_table_field(db, table_name, table_key, field_name):
    seperator = db['seperator']
    # print(db, table_name, table_key, field_name)
    return db[table_name+seperator+table_key][field_name]

def get_db_table_fields(db, table_name, table_key):
    seperator = db['seperator']
    return db[table_name+seperator+table_key]

def get_db_table_keys(db, table_name):
    result = []
    for key in db.keys():
        if key.startswith(table_name):
            result.append(key[len(table_name)+1:])
    return result


def get_state_db_by_slot(slot_id):
    return connect_muti_db_common(slot_id, DB_STATE_IDX) 

def get_counter_db_by_slot(slot_id):
    return connect_muti_db_common(slot_id, DB_COUNTER_IDX) 

def get_config_db_by_slot(slot_id):
    return connect_muti_db_common(slot_id, DB_CONFIG_IDX) 

def get_history_db_by_slot(slot_id):
    return connect_muti_db_common(slot_id, DB_HISTORY_IDX) 

def get_chassis_state_db():
    return get_state_db_by_slot(0) 

def get_chassis_counter_db():
    return get_counter_db_by_slot(0) 

def get_chassis_config_db():
    return get_config_db_by_slot(0) 

def get_chassis_history_db():
    return get_history_db_by_slot(0) 

def subscribe_channel(db, channel, timeout):
    return 0, ''

def load_slots_mock_data():
    test_path = os.path.dirname(otn.utils.__file__)
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
