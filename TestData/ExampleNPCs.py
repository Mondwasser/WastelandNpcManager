from Data.Ability import Ability, Ability_Type
from Data.NPC import NPC
from Data.Skills import Skills
from Data.Weapon import Weapon, ShootingRange, Rarity

KER = NPC(
    name = "Ker",
    strength = 3,
    toughness = 3,
    agility = 4,
    initiative = 6,
    willpower = 2,
    intelligence = 1,
    fellowship = 1,
    resilience = 7,
    armor = 2,
    armour_name = "Bodyglove",
    defense = 5,
    wounds = 6,
    shocks = 3,
    determination = 4,
    conviction = 2,
    resolve = 1,
    speed = 6,
    size = "Avg",
    keywords = ["Imperial", "Necronkultist"],
    skills = Skills(
        default = 6,
        awareness = 4,
        survival = 4,
        tech = 5,
        weapon_skill = 2,
        stealth = 4,
        intimidation = 5
    ),

    abilities = [
        Ability(
            Ability_Type.PASSIVE,
            "Paineditor",
            "No penalties for wounds or exhaustion")
    ],

    weapons = [
        Weapon(
            name = "Stubber",
            damage = 7,
            extra_dice= 1,
            is_strength_based=False,
            armor_penetration= 0,
            salvo= 1,
            range = ShootingRange(6,12,18),
            traits = [ "Pistol" ],
            rarity= Rarity.VERY_RARE,
            value= 4
        ),
        Weapon(
            name = "Shock Maul",
            damage = 4,
            extra_dice= 4,
            is_strength_based=True,
            armor_penetration= 0,
            salvo= 0,
            range = None,
            traits = [ "Agonising", "Brutal" ],
            rarity= Rarity.VERY_RARE,
            value= 4
        )
    ]

)