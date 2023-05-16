
def thrift_set_slot_power(slot_id,value):
    print(f"thrift set {slot_id} value {value}")
    
def thrift_config_fan_speed(fan_id, speed):
    print(f"thrift set {fan_id} speed {speed}")

def thrift_clear_chassis_pm(pm_type):
    print(f"thrift clear chassis-1 pm {pm_type}")
    
def thrift_clear_fan_pm(fan_id, pm_type):
    print(f"thrift clear fan-{fan_id} pm {pm_type}")

def thrift_clear_psu_pm(psu_id, pm_type):
    print(f"thrift clear psu-{psu_id} pm {pm_type}")