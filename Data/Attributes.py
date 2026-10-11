from enum import Enum

class Attribute(str, Enum):
    """All attributes in the Wrath&Glory ruleset"""
    NONE = "none"
    STRENGTH = "strength"
    TOUGHNESS = "toughness"
    AGILITY = "agility"
    INITIATIVE = "initiative"
    WILLPOWER = "willpower"
    INTELLIGENCE = "intelligence"
    FELLOWSHIP = "fellowship"