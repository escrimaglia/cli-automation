# Data Models Service Classes
# Ed Scrimaglia

from pydantic import BaseModel, Field
from typing import List

class Device(BaseModel):
    host: str
    username: str
    password: str
    secret: str | None = None
    device_type: str
    global_delay_factor: float = Field(default=.1)
    port: int | None = Field(default=22)
    ssh_config_file: str | None = None

class ModelSingleSsh(BaseModel):
    device: Device
    commands: List[str]

class TelnetPush(BaseModel):
    device: Device
    commands: List[str]

class ModelTelnetPush(BaseModel):
    device: List[TelnetPush]

class ModelTelnetPull(BaseModel):
    devices: List[Device]
    command: str

class MultipleSsh(BaseModel):
    device: Device
    commands: List[str]

class ModelMultipleSsh(BaseModel):
    device: List[MultipleSsh]
