from dataclasses import dataclass, field
from Data.Ability import Ability
from Data.Skills import Skills
from Data.Weapon import Weapon

@dataclass
class NPC:
    """Represents a NPC in the Wrath&Glory ruleset with homebrew additions"""
    name : str
    strength : int
    toughness : int
    agility : int
    initiative : int
    willpower : int
    intelligence : int
    fellowship : int
    resilience : int
    armor : int
    armour_name : str
    defense : int
    wounds : int
    shocks : int
    determination : int
    conviction : int
    resolve : int
    speed : int
    size : str
    keywords : list[str] = field(default_factory=list)
    skills : Skills = field(default_factory=Skills)
    abilities : list[Ability] = field(default_factory=list)
    weapons : list[Weapon] = field(default_factory=list)
