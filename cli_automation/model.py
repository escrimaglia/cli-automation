from pydantic import BaseModel, Field
from typing import List

class Devices(BaseModel):
    host: str
    username: str
    password: str
    device_type: str
    port: int | None = Field(default=22)
    ssh_config_file: str | None = None

class Model(BaseModel):
    devices: List[Devices]
    commands: List[str]

class ModelPush(BaseModel):
    devices: Devices
    commands: List[str]