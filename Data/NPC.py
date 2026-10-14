import json
from dataclasses import dataclass, field, asdict

from PySide6.QtGui import QPixmap

from Data.Ability import Ability
from Data.Attributes import Attribute
from Data.Skills import Skills, map_skill_to_attribute
from Data.Weapon import Weapon

class InvalidSkillNameException(Exception):
    """Exception raised when skill name was invalid"""

    def __init__(self, skill_name: str):
        self.message = f"Skill name {skill_name} was invalid."
        super().__init__(self.message)

@dataclass
class NPC:
    """Represents a NPC in the Wrath&Glory ruleset with homebrew additions"""
    name : str
    group : str
    strength : int
    toughness : int
    agility : int
    initiative : int
    willpower : int
    intelligence : int
    fellowship : int
    resilience : int
    armor : int
    armor_name : str
    defense : int
    wounds : int
    shock : int
    determination : int
    conviction : int
    resolve : int
    speed : int
    size : str
    picture_url : str
    picture : QPixmap | None = None
    keywords : list[str] = field(default_factory=list)
    faction_keywords : list[str] = field(default_factory=list)
    skills : Skills = field(default_factory=Skills)
    abilities : list[Ability] = field(default_factory=list)
    weapons : list[Weapon] = field(default_factory=list)
    id : str = field(default_factory=str)

    def to_json(self) -> str:
        """Turns class into json-format"""
        return json.dumps(asdict(self))

    def get_skill_dice_pool_value(self, skill_name) -> int:
        """Returns the value of complete skill dice pool for the character"""
        if not skill_name in map_skill_to_attribute:
            raise InvalidSkillNameException(skill_name)

        if map_skill_to_attribute[skill_name] == Attribute.NONE:
            return  getattr(self.skills, skill_name)

        return getattr(self, map_skill_to_attribute[skill_name]) + getattr(self.skills, skill_name)

    @classmethod
    def from_dict(cls, data: dict) -> NPC:
        """Creates a NPC object from a dictionary"""
        new_npc = cls(
            name=data["name"],
            strength=data["strength"],
            toughness=data["toughness"],
            agility=data["agility"],
            initiative=data["initiative"],
            willpower=data["willpower"],
            intelligence=data["intelligence"],
            fellowship=data["fellowship"],
            resilience=data["resilience"],
            armor=data["armor"],
            armor_name=data["armor_name"],
            defense=data["defense"],
            wounds=data["wounds"],
            shock=data["shock"],
            determination=data["determination"],
            conviction=data["conviction"],
            resolve=data["resolve"],
            speed=data["speed"],
            size=data["size"],
            keywords=data["keywords"],
            faction_keywords=data["faction_keywords"],
            skills=Skills.from_dict(data["skills"]),
            weapons = [],
            abilities = [],
            picture_url=data["picture_url"],
            group = data["group"]
        )

        for ability in data["abilities"]:
            new_npc.abilities.append(Ability.from_dict(ability))
        for weapon in data["weapons"]:
            new_npc.weapons.append(Weapon.from_dict(weapon))

        return new_npc