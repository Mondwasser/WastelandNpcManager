from dataclasses import dataclass
from Data.Attributes import Attribute

map_skill_to_attribute = {
    "default" : Attribute.NONE,
    "athletics" : Attribute.STRENGTH,
    "awareness" : Attribute.INTELLIGENCE,
    "ballistic" : Attribute.AGILITY,
    "cunning" : Attribute.FELLOWSHIP,
    "deception" : Attribute.FELLOWSHIP,
    "insight" : Attribute.FELLOWSHIP,
    "intimidation" : Attribute.WILLPOWER,
    "investigation" : Attribute.INTELLIGENCE,
    "leadership" : Attribute.FELLOWSHIP,
    "medicae" : Attribute.INTELLIGENCE,
    "persuasion" : Attribute.FELLOWSHIP,
    "pilot" : Attribute.AGILITY,
    "psychic_mastery" : Attribute.WILLPOWER,
    "scholar" : Attribute.INTELLIGENCE,
    "stealth" : Attribute.AGILITY,
    "survival" : Attribute.WILLPOWER,
    "tech" : Attribute.INTELLIGENCE,
    "weapon_skill" : Attribute.INITIATIVE
}

@dataclass
class Skills:
    default : int
    athletics : int = 0
    awareness : int = 0
    ballistic : int = 0
    cunning : int = 0
    deception : int = 0
    insight : int = 0
    intimidation : int = 0
    investigation : int = 0
    leadership : int = 0
    medicae : int = 0
    persuasion : int = 0
    pilot : int = 0
    psychic_mastery : int = 0
    scholar : int = 0
    stealth : int = 0
    survival : int = 0
    tech : int = 0
    weapon_skill : int = 0