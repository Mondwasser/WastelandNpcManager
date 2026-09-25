from enum import Enum

class Attribute(str, Enum):
    NONE = "none"
    STRENGTH = "strength"
    TOUGHNESS = "toughness"
    AGILITY = "agility"
    INITIATIVE = "initiative"
    WILLPOWER = "willpower"
    INTELLIGENCE = "intelligence"
    FELLOWSHIP = "fellowship"