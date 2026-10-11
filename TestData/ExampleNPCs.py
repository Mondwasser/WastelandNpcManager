from PySide6.QtGui import QPixmap

from Data.Ability import Ability, Ability_Type
from Data.NPC import NPC
from Data.Skills import Skills
from Data.Weapon import Weapon, ShootingRange, Rarity, MeleeRange

KER = NPC(
    name = "Ker",
    group = "Necromancer",
    picture= None,
    picture_url= "TestData/Cyberchar.jpeg",
    strength = 3,
    toughness = 3,
    agility = 4,
    initiative = 6,
    willpower = 2,
    intelligence = 1,
    fellowship = 1,
    resilience = 7,
    armor = 2,
    armor_name="Bodyglove",
    defense = 5,
    wounds = 6,
    shock= 3,
    determination = 4,
    conviction = 2,
    resolve = 1,
    speed = 6,
    size = "Avg",
    keywords = ["Imperial", "Necronkultist"],
    faction_keywords= ["Mechanic"],
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
            group= "Projectile Weapons",
            is_melee= False,
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
            group= "Exotic Melee weapons",
            is_melee= True,
            damage = 4,
            extra_dice= 4,
            is_strength_based=True,
            armor_penetration= 0,
            salvo= 0,
            range = MeleeRange(),
            traits = [ "Agonising", "Brutal" ],
            rarity= Rarity.VERY_RARE,
            value= 4
        )
    ]
)
Skarn = NPC(
    name = "Skarn",
    group = "Raider Steinkatzen",
    picture= None,
    picture_url= "TestData/Cyberchar.jpeg",
    strength = 3,
    toughness = 3,
    agility = 4,
    initiative = 5,
    willpower = 4,
    intelligence = 2,
    fellowship = 2,
    resilience = 7,
    armor = 1,
    armor_name="Assorted Armor",
    defense = 4,
    wounds = 7,
    shock= 5,
    determination = 4,
    conviction = 3,
    resolve = 2,
    speed = 8,
    size = "Avg",
    keywords = ["Raider"],
    faction_keywords= ["Raider", "Leader"],
    skills = Skills(
        default = 4,
        awareness = 6,
        weapon_skill = 7,
        athletics = 5
    ),

    abilities = [
        Ability(
            Ability_Type.PASSIVE,
            "Glancing Blow",
            "You may use your Agility instead of your Toughness when you roll Determination against Damage from attacks, and may roll Determination against Mortal Wounds.\nYou cannot use this ability if you are immobilised in some way, such as through the Restrained Condition."
        ),
        Ability(
            Ability_Type.PASSIVE,
            "Defensive blademaster",
            "Gets +2 defence against melee, for a total of +3 because of his swords parry"
        ),
        Ability(
            Ability_Type.PASSIVE,
            "Find the gap",
            "His melee weapons get +2 Rending"
        )

    ],

    weapons = [
        Weapon(
            name = "Splinter Pistol",
            group= "Aeldari ranged weapons",
            is_melee= False,
            damage = 7,
            extra_dice= 1,
            is_strength_based=False,
            armor_penetration= 0,
            salvo= 1,
            range = ShootingRange(6,12,18),
            traits = [ "Pistol", "Inflict(Poisoned 3)" ],
            rarity= Rarity.UNIQUE,
            value= 4
        ),
        Weapon(
            name = "Eldar Blade",
            group= "Aeldari melee weapons",
            is_melee= True,
            damage = 4,
            extra_dice= 4,
            is_strength_based=True,
            armor_penetration= -1,
            salvo= 0,
            range= MeleeRange(),
            traits = [ "Rending (2)" ],
            rarity= Rarity.UNIQUE,
            value= 4
        ),
        Weapon(
            name = "Knife",
            group= "Melee weapons",
            is_melee= True,
            damage = 2,
            extra_dice= 2,
            is_strength_based=True,
            armor_penetration= 0,
            salvo= 0,
            range = MeleeRange(strength_multiplier_for_throw=4),
            traits = [ "Rending (2)" ],
            rarity= Rarity.UNIQUE,
            value= 4
        )
    ]
)

