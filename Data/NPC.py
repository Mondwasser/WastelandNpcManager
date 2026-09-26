import json
from dataclasses import dataclass, field, asdict
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
    id : str = field(default_factory=str)

    def to_json(self):
        """Turns class into json-format"""
        return json.dumps(asdict(self))

    @classmethod
    def from_dict(cls, data: dict):
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
            armour_name=data["armour_name"],
            defense=data["defense"],
            wounds=data["wounds"],
            shocks=data["shocks"],
            determination=data["determination"],
            conviction=data["conviction"],
            resolve=data["resolve"],
            speed=data["speed"],
            size=data["size"],
            keywords=data["keywords"],
            skills=Skills.from_dict(data["skills"]),
            weapons = [],
            abilities = [],
        )

        for ability in data["abilities"]:
            new_npc.abilities.append(Ability.from_dict(ability))
        for weapon in data["weapons"]:
            new_npc.weapons.append(Weapon.from_dict(weapon))

        return new_npc
