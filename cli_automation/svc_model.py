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

class Model(BaseModel):
    devices: List[Device]
    commands: List[str]

class ModelSsh(BaseModel):
    devices: List[Device]
    commands: List[str]

class ModelTelnetPush(BaseModel):
    devices: List[Device]
    commands: List[str]

class ModelTelnetPull(BaseModel):
    devices: List[Device]
    command: str