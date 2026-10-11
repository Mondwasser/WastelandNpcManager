from dataclasses import dataclass
from enum import StrEnum

class Ability_Type(StrEnum):
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
    def from_dict(cls, data: dict) -> Ability:
        return cls(
            ability_type=data["ability_type"],
            name=data["name"],
            text=data["text"]
        )