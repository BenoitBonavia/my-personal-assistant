from typing import Optional
from typing import List

from pydantic import BaseModel

class HueLightConfigurationType(BaseModel):
    id: str
    room: str
    name: str
    paired: List[int] = []
    details: Optional[str] = None

class HueConfigurationType(BaseModel):
    bridge_ip: str
    manager_name: str
    manager_description: str
    hue_lights: list[HueLightConfigurationType]
