from dataclasses import dataclass, field


@dataclass
class Range:
    short : int = 0
    medium : int = 0
    long : int = 0

@dataclass
class Weapon:
    name : str
    damage : int
    is_strength_based : bool
    range : Range
    extra_dice : int
    armor_penetration : int
    salvo : int
    traits : list[str] = field(default_factory=list)

