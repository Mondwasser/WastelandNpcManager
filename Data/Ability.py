from dataclasses import dataclass
from enum import Enum

class Ability_Type(str,Enum):
    """All types of abilities in the Wrath&Glory ruleset"""
    BATTLECRY = "Battlecry"
    ACTION = "Action"
    RUIN = "Ruin"
    WRATH = "Wrath"
    COMPLICATION = "Complication"
    REACTION = "Reaction"
    DETERMINATION = "Determination"
    ANNIHILATION = "Annihilation"
    PASSIVE = "Passive"

@dataclass
class Ability:
    """Represents an ability in the Wrath&Glory ruleset"""
    ability_type: str
    name: str
    text: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            ability_type=data["ability_type"],
            name=data["name"],
            text=data["text"]
        )