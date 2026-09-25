from dataclasses import dataclass
from enum import Enum

class Ability_Type(Enum):
    """All types of abilities in the Wrath&Glory ruleset"""
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
    """Represents an ability in the Wrath&Glory ruleset"""
    ability_type: Ability_Type
    name: str
    text: str