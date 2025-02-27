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
    juniper_junos = "juniper_junos"
    arista_eos = "arista_eos"
    huawei = "huawei"
    nokia_sros = "alcatel_sros"
