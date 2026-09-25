from dataclasses import dataclass
from enum import Enum

class Ability_Type(Enum):
    BATTLECRY = 0
    ACTION = 1
    RUIN = 2
    WRATH = 3
    COMPLICATION = 4
    REACTION = 5
    DETERMINATION = 6
    ANNIHILATION = 7
    PASSIVE = 8

@dataclass
class Ability:
    ability_type: Ability_Type
    name: str
    text: str