from enum import Enum

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
    alcatel_sros = "alcatel_sros"
    vyos = "vyos"
    vyatta_vyos = "vyatta_vyos"
    extreme_exos = "extreme_exos"
    extreme = "extreme"