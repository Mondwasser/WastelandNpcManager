from Data.Weapon import Weapon, Range, ShootingRange, MeleeRange, Rarity

exampleGun = Weapon(name="Lasrifle",
                    damage=7, is_strength_based=False, is_melee=False, extra_dice=1,
                    salvo=2, armor_penetration=0, range=ShootingRange(12, 24, 36),
                    traits=["Rapid Fire (1)", "Reliable"], value=3, rarity=Rarity.COMMON)
exampleMelee = Weapon(name="Knife",
                      damage=2, is_strength_based=True, is_melee=True, extra_dice=2,
                      salvo=0, armor_penetration=0, range=MeleeRange(1,4),
                      traits=["Reliable"], value=2, rarity=Rarity.COMMON)