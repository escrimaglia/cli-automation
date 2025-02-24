from pydantic import BaseModel, Field
from typing import List

class Device(BaseModel):
    host: str
    username: str
    password: str
    device_type: str
    port: int | None = Field(default=22)
    ssh_config_file: str | None = None

class Model(BaseModel):
    devices: List[Device]
    commands: List[str]

class ModelSshPush(BaseModel):
    device: Device
    commands: List[str]

class ModelSshPull(BaseModel):
    device: Device
    commands: List[str]

class ModelTelnetPush(BaseModel):
    device: Device
    commands: List[str]

class ModelTelnetPull(BaseModel):
    devices: List[Device]
    command: str