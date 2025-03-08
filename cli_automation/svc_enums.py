from enum import Enum

class Logging(Enum):
    info = "INFO"
    debug = "DEBUG"
    error = "ERROR"
    warning = "WARNING"
    critical = "CRITICAL"

class DeviceType(Enum):
    cisco_ios = "cisco_ios"
    cisco_xr = "cisco_xr"
    cisco_xe = "cisco_xe"
    cisco_nxos = "cisco_nxos"
    juniper = "juniper"
    juniper_junos = "juniper_junos"
    arista_eos = "arista_eos"
    huawei = "huawei"
    huawei_vrp = "huawei_vrp"
    nokia_sros = "alcatel_sros"
    extreme_exos = "extreme_exos"
    vyos = "vyos"
    vyatta_vyos = "vyatta_vyos"
    a10 = "a10"
   
    

