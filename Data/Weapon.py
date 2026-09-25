from dataclasses import dataclass, field, asdict
from enum import Enum
import json

@dataclass
class Range:
    """Base class for shooting and throwing ranges"""
    def to_dict(self):
        return asdict(self)

    @classmethod
    def cls_from_dict(cls, data: dict):
        """Creates an instance of the correct subclass from a dict"""
        if data is None or not data.__contains__("class_name"):
            raise TypeError(f"Unrecognized data type: {data}")
        match data["class_name"]:
            case "ShootingRange":
                return ShootingRange.cls_from_dict(data)
            case "ThrowingRange":
                return ThrowingRange.cls_from_dict(data)
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
    def cls_from_dict(cls, data: dict):
        """Creates an instance from a dict"""
        return cls(
        short = data["short"],
        medium = data["medium"],
        long = data["long"])

@dataclass
class ThrowingRange(Range):
    """Class representing ranges for throwing"""
    strength_multiplier : int
    class_name : str = field(default="ThrowingRange", init=False)

    @classmethod
    def cls_from_dict(cls, data: dict):
        """Creates an instance from a dict"""
        return  cls(strength_multiplier= data["strength_multiplier"])

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
    damage : int
    is_strength_based : bool
    range : Range
    extra_dice : int
    armor_penetration : int
    salvo : int
    value : int
    rarity : Rarity
    id : str = field(default_factory=str)
    traits : list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict):
        """Creates an instance from a dict"""
        return cls(
            name = data["name"],
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

    def to_dict(self):
        """Turns class into a dict"""
        return {
            "name" : self.name,
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