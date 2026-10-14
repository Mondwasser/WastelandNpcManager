from dataclasses import dataclass, field, asdict
from enum import Enum
import json

@dataclass
class Range:
    """Base class for shooting and throwing ranges"""
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def cls_from_dict(cls, data: dict) -> Range:
        """Creates an instance of the correct subclass from a dict"""
        if data is None:
            return None
        elif not data.__contains__("class_name"):
            raise TypeError(f"Unrecognized data type: {data}")
        match data["class_name"]:
            case "ShootingRange":
                return ShootingRange.cls_from_dict(data)
            case "MeleeRange":
                return MeleeRange.cls_from_dict(data)
            case _:
                raise TypeError(f"Unrecognized data type: {data}")

@dataclass
class ShootingRange(Range):
    """Class representing ranges for shooting"""
    short : int = 0
    medium : int = 0
    long : int = 0
    class_name : str = field(default="ShootingRange", init=False)

    @classmethod
    def cls_from_dict(cls, data: dict) -> ShootingRange:
        """Creates an instance from a dict"""
        return cls(
            short = data["short"],
            medium = data["medium"],
            long = data["long"])

@dataclass
class MeleeRange(Range):
    """Class representing ranges for melee with option to be thwrowable"""
    strength_multiplier_for_throw : int = field(default=0)
    """If value is 0, weapon can not be thrown"""
    melee_range : int = field(default=1)
    class_name : str = field(default="MeleeRange", init=False)

    @classmethod
    def cls_from_dict(cls, data: dict) -> MeleeRange:
        """Creates an instance from a dict"""
        return  cls(
            strength_multiplier_for_throw= data["strength_multiplier_for_throw"],
            melee_range = data["melee_range"])

class Rarity(str,Enum):
    """Class representing rarity"""
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    VERY_RARE = "Very Rare"
    UNIQUE = "Unique"

@dataclass
class Weapon:
    """Represents a weapon in the Wrath&Glory ruleset"""
    name : str
    is_melee : bool
    group : str
    damage : int
    is_strength_based : bool
    extra_dice : int
    armor_penetration : int
    salvo : int
    value : int
    rarity : Rarity
    range : Range = field(default_factory=Range)
    id : str = field(default_factory=str)
    traits : list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> Weapon:
        """Creates an instance from a dict"""
        return cls(
            name = data["name"],
            group= data["group"],
            is_melee = data["is_melee"],
            damage = data["damage"],
            is_strength_based = data["is_strength_based"],
            range = Range.cls_from_dict(data["range"]),
            extra_dice = data["extra_dice"],
            armor_penetration = data["armor_penetration"],
            salvo = data["salvo"],
            value = data["value"],
            rarity = data["rarity"],
            id = data["id"],
            traits = data["traits"]
        )

    def to_dict(self) -> dict:
        """Turns class into a dict"""
        return {
            "name" : self.name,
            "group" : self.group,
            "is_melee" : self.is_melee,
            "damage" : self.damage,
            "is_strength_based" : self.is_strength_based,
            "range" : self.range.to_dict(),
            "extra_dice" : self.extra_dice,
            "armor_penetration" : self.armor_penetration,
            "salvo" : self.salvo,
            "value" : self.value,
            "rarity" : self.rarity,
            "id" : self.id,
            "traits" : self.traits
        }

    def to_json(self):
        """Turns class into json-format"""
        return json.dumps(asdict(self))