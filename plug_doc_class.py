from dataclasses import dataclass
from typing import List, Any

@dataclass
class PlugDocClass:
    name: str
    description: str
    functions: List[Any]