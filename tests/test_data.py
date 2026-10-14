"""Offline tests for Data models; expected failures identify existing defects."""

import json
import unittest
from dataclasses import asdict, fields
from typing import get_type_hints

from Data.Ability import Ability, Ability_Type
from Data.Attributes import Attribute
from Data.IsGroupable import HasGroup
from Data.NPC import NPC, InvalidSkillNameException
from Data.Skills import Skills, map_skill_to_attribute
from Data.Weapon import MeleeRange, Range, Rarity, ShootingRange, Weapon


def skill_data():
    return {name: index for index, name in enumerate(map_skill_to_attribute)}


def weapon_data():
    return dict(name="Lasrifle", is_melee=False, group="Imperium", damage=7,
                is_strength_based=False, extra_dice=1, armor_penetration=-1,
                salvo=2, value=3, rarity=Rarity.COMMON,
                range=ShootingRange(12, 24, 36), id="weapon-1",
                traits=["Reliable"])


def npc_data():
    return dict(name="Guard", group="Imperium", strength=2, toughness=3,
                agility=4, initiative=5, willpower=6, intelligence=7,
                fellowship=8, resilience=9, armor=2, armor_name="Flak",
                defense=3, wounds=10, shock=5, determination=2,
                conviction=3, resolve=4, speed=6, size="Medium",
                picture_url="", skills=Skills(**skill_data()))


def npc_payload():
    result = asdict(NPC(**npc_data()))
    result["armor_name"] = result.pop("armor_name")
    result["shock"] = result.pop("shock")
    return result


class EnumTests(unittest.TestCase):
    def test_all_values(self):
        # Verify every declared enum value can be reconstructed and behaves as a string.
        expected = {
            Ability_Type: ["Battlecry", "Action", "Ruin", "Wrath", "Complication",
                           "Reaction", "Determination", "Annihilation", "Passive"],
            Attribute: ["none", "strength", "toughness", "agility", "initiative",
                        "willpower", "intelligence", "fellowship"],
            Rarity: ["Common", "Uncommon", "Rare", "Very Rare", "Unique"],
        }
        for enum, values in expected.items():
            with self.subTest(enum=enum):
                self.assertEqual([member.value for member in enum], values)
            for value in values:
                with self.subTest(enum=enum, value=value):
                    member = enum(value)
                    self.assertIsInstance(member, str)
                    self.assertEqual(member, value)

    def test_invalid_values(self):
        # Verify empty, unknown, incorrectly cased, and non-string enum values are rejected.
        for enum in (Ability_Type, Attribute, Rarity):
            for value in ("", "unknown", None, 123, next(iter(enum)).value.upper()):
                with self.subTest(enum=enum, value=value):
                    with self.assertRaises(ValueError):
                        enum(value)


class AbilityTests(unittest.TestCase):
    def test_from_dict_preserves_fields(self):
        # Verify ability deserialization preserves all fields, including empty and Unicode text.
        for kind in Ability_Type:
            for name, text in (("War cry", "Gain +1 die."), ("", ""), ("怒り", "Line 1\nLine 2")):
                with self.subTest(kind=kind, name=name):
                    data = dict(ability_type=kind, name=name, text=text)
                    self.assertEqual(asdict(Ability.from_dict(data)), data)

    def test_missing_fields(self):
        # Verify omitting any required ability field raises KeyError for that field.
        data = dict(ability_type="Action", name="Strike", text="Attack")
        for key in data:
            with self.subTest(key=key):
                with self.assertRaises(KeyError) as error:
                    Ability.from_dict({k: v for k, v in data.items() if k != key})
                self.assertEqual(error.exception.args, (key,))

    def test_invalid_container(self):
        # Verify ability deserialization rejects non-dictionary containers.
        for data in (None, 1, []):
            with self.subTest(data=data), self.assertRaises(TypeError):
                Ability.from_dict(data)

    def test_annotations_do_not_validate_values(self):
        # Verify the current model accepts field values that violate its type annotations.
        # Existing behavior: dataclass annotations impose no runtime validation.
        data = dict(ability_type="Unknown", name=None, text=123)
        self.assertEqual(asdict(Ability.from_dict(data)), data)


class SkillsTests(unittest.TestCase):
    def test_defaults_and_required_default(self):
        # Verify named skills default to zero and the default skill value is required.
        skills = Skills(default=2)
        self.assertEqual(skills.default, 2)
        for item in fields(Skills):
            if item.name != "default":
                self.assertEqual(getattr(skills, item.name), 0)

    def test_from_dict_preserves_every_skill(self):
        # Verify deserialization preserves the value of every skill.
        self.assertEqual(asdict(Skills.from_dict(skill_data())), skill_data())

    def test_missing_each_skill(self):
        # Verify omitting any skill from the input raises KeyError for that skill.
        for name in skill_data():
            data = skill_data()
            del data[name]
            with self.subTest(name=name), self.assertRaises(KeyError) as error:
                Skills.from_dict(data)
            self.assertEqual(error.exception.args, (name,))

    def test_invalid_container(self):
        # Verify skills deserialization rejects non-dictionary containers.
        for data in (None, 1, []):
            with self.subTest(data=data), self.assertRaises(TypeError):
                Skills.from_dict(data)

    def test_mapping(self):
        # Verify every skill has the correct attribute mapping and no skill is omitted.
        expected = {
            "default": "none", "athletics": "strength", "awareness": "intelligence",
            "ballistic": "agility", "cunning": "fellowship", "deception": "fellowship",
            "insight": "fellowship", "intimidation": "willpower",
            "investigation": "intelligence", "leadership": "fellowship",
            "medicae": "intelligence", "persuasion": "fellowship", "pilot": "agility",
            "psychic_mastery": "willpower", "scholar": "intelligence",
            "stealth": "agility", "survival": "willpower", "tech": "intelligence",
            "weapon_skill": "initiative",
        }
        self.assertEqual(map_skill_to_attribute, expected)
        self.assertEqual(set(expected), {item.name for item in fields(Skills)})

    def test_numeric_and_type_validation_is_not_enforced(self):
        # Verify negative and incorrectly typed skill values are currently accepted.
        for value in (-1, None, "invalid"):
            with self.subTest(value=value):
                data = {name: value for name in skill_data()}
                self.assertEqual(asdict(Skills.from_dict(data)), data)


class RangeTests(unittest.TestCase):
    def test_defaults_and_serialization(self):
        # Verify each range class serializes its default values and discriminator.
        self.assertEqual(Range().to_dict(), {})
        self.assertEqual(ShootingRange().to_dict(),
                         dict(short=0, medium=0, long=0, class_name="ShootingRange"))
        self.assertEqual(MeleeRange().to_dict(), dict(strength_multiplier_for_throw=0,
                         melee_range=1, class_name="MeleeRange"))

    def test_shooting_round_trip(self):
        # Verify zero and nonzero shooting ranges survive dictionary round trips.
        for values in ((0, 0, 0), (12, 24, 36)):
            with self.subTest(values=values):
                original = ShootingRange(*values)
                self.assertEqual(Range.cls_from_dict(original.to_dict()), original)

    def test_none_range(self):
        # Verify a null range payload produces no range object.
        self.assertIsNone(Range.cls_from_dict(None))

    def test_invalid_discriminator(self):
        # Verify missing, unknown, empty, and null range discriminators are rejected.
        for data in ({}, {"class_name": "Unknown"}, {"class_name": None},
                     {"class_name": ""}):
            with self.subTest(data=data), self.assertRaises(TypeError):
                Range.cls_from_dict(data)

    def test_missing_range_values(self):
        # Verify each range reader rejects payloads missing a required range value.
        for cls, data in ((ShootingRange, dict(short=1, medium=2, long=3)),
                          (MeleeRange, dict(strength_multiplier=2, melee_range=1))):
            for key in data:
                with self.subTest(cls=cls, key=key), self.assertRaises(KeyError):
                    cls.cls_from_dict({k: v for k, v in data.items() if k != key})

    def test_invalid_subclass_input(self):
        # Verify both concrete range readers reject non-dictionary containers.
        for cls in (ShootingRange, MeleeRange):
            for data in (None, 1, []):
                with self.subTest(cls=cls, data=data), self.assertRaises(TypeError):
                    cls.cls_from_dict(data)

    def test_melee_factory_round_trip(self):
        # Verify the range factory can reconstruct a serialized melee range
        original = MeleeRange(2, 3)
        self.assertEqual(Range.cls_from_dict(original.to_dict()), original)

    def test_melee_subclass_round_trip(self):
        # Verify the melee range reader can read its own serialized keys;
        original = MeleeRange(2, 3)
        self.assertEqual(MeleeRange.cls_from_dict(original.to_dict()), original)


class WeaponTests(unittest.TestCase):
    def test_field_types_are_not_validated(self):
        # Verify weapon construction currently accepts incorrectly typed field values.
        data = weapon_data()
        data.update(damage="invalid", rarity="Unknown", is_melee=None)
        weapon = Weapon(**data)
        self.assertEqual(weapon.damage, "invalid")
        self.assertEqual(weapon.rarity, "Unknown")
        self.assertIsNone(weapon.is_melee)

    def test_non_serializable_value(self):
        # Verify JSON serialization rejects a trait value that JSON cannot encode.
        data = weapon_data()
        data["traits"] = [object()]
        with self.assertRaises(TypeError):
            Weapon(**data).to_json()

    def test_constructor_preserves_fields(self):
        # Verify weapon construction preserves every supplied field.
        data = weapon_data()
        weapon = Weapon(**data)
        for key, value in data.items():
            self.assertEqual(getattr(weapon, key), value)

    def test_required_constructor_fields(self):
        # Verify omitting any required weapon constructor argument raises TypeError.
        optional = {"range", "id", "traits"}
        for key in weapon_data().keys() - optional:
            data = weapon_data()
            del data[key]
            with self.subTest(key=key), self.assertRaises(TypeError):
                Weapon(**data)

    def test_mutable_defaults_are_independent(self):
        # Verify weapons receive separate range and traits defaults and an empty ID.
        data = {k: v for k, v in weapon_data().items() if k not in {"range", "id", "traits"}}
        first, second = Weapon(**data), Weapon(**data)
        self.assertEqual(first.id, "")
        self.assertIsInstance(first.range, Range)
        self.assertIsNot(first.range, second.range)
        first.traits.append("Reliable")
        self.assertEqual(second.traits, [])

    def test_to_dict(self):
        # Verify the current weapon dictionary format and nested range serialization.
        result = Weapon(**weapon_data()).to_dict()
        expected = weapon_data()
        expected["range"] = expected["range"].to_dict()
        self.assertEqual(result, expected)

    def test_json_preserves_all_fields(self):
        # Verify weapon JSON preserves all fields for base, shooting, and melee ranges.
        for distance in (Range(), ShootingRange(12, 24, 36), MeleeRange(2, 1)):
            with self.subTest(distance=distance):
                data = weapon_data()
                data["range"] = distance
                weapon = Weapon(**data)
                self.assertEqual(json.loads(weapon.to_json()), asdict(weapon))

    def test_missing_deserialization_fields(self):
        # Verify missing fields read by the weapon deserializer raise the matching KeyError.
        payload = json.loads(Weapon(**weapon_data()).to_json())
        for key in payload.keys() - {"is_melee", "group"}:
            data = dict(payload)
            del data[key]
            with self.subTest(key=key), self.assertRaises(KeyError) as error:
                Weapon.from_dict(data)
            self.assertEqual(error.exception.args, (key,))

    def test_invalid_payload(self):
        # Verify weapon deserialization rejects malformed containers and unknown range types.
        for data in (None, 1, []):
            with self.subTest(data=data), self.assertRaises(TypeError):
                Weapon.from_dict(data)
        data = json.loads(Weapon(**weapon_data()).to_json())
        data["range"] = {"class_name": "Unknown"}
        with self.assertRaises(TypeError):
            Weapon.from_dict(data)

    def test_from_dict_valid_payload(self):
        # Verify a complete weapon payload reconstructs the original weapon; currently broken.
        # from_dict fails to pass required group and is_melee arguments.
        weapon = Weapon(**weapon_data())
        self.assertEqual(Weapon.from_dict(json.loads(weapon.to_json())), weapon)

    def test_to_dict_preserves_group_and_melee_flag(self):
        # Verify weapon dictionaries include group and melee status; currently broken.
        result = Weapon(**weapon_data()).to_dict()
        self.assertEqual((result["group"], result["is_melee"]), ("Imperium", False))


class NPCTests(unittest.TestCase):
    def test_non_serializable_picture(self):
        # Verify NPC JSON serialization rejects a picture object that JSON cannot encode.
        npc = NPC(**npc_data(), picture=object())
        with self.assertRaises(TypeError):
            npc.to_json()

    def test_required_constructor_fields(self):
        # Verify omitting any required NPC constructor argument raises TypeError.
        for key in npc_data().keys() - {"skills"}:
            data = npc_data()
            del data[key]
            with self.subTest(key=key), self.assertRaises(TypeError):
                NPC(**data)

    def test_constructor_and_defaults(self):
        # Verify NPC construction preserves supplied fields and initializes optional defaults.
        data = npc_data()
        npc = NPC(**data)
        for key, value in data.items():
            self.assertEqual(getattr(npc, key), value)
        self.assertIsNone(npc.picture)
        self.assertEqual(npc.id, "")
        for key in ("keywords", "faction_keywords", "abilities", "weapons"):
            self.assertEqual(getattr(npc, key), [])

    def test_mutable_defaults_are_independent(self):
        # Verify NPC keyword, faction, ability, and weapon lists are not shared.
        first, second = NPC(**npc_data()), NPC(**npc_data())
        for key in ("keywords", "faction_keywords", "abilities", "weapons"):
            with self.subTest(key=key):
                getattr(first, key).append("sentinel")
                self.assertEqual(getattr(second, key), [])

    def test_all_named_skill_dice_pools(self):
        # Verify each named skill adds its mapped attribute and handles zero values.
        expected = dict(athletics=3, awareness=9, ballistic=7, cunning=12,
                        deception=13, insight=14, intimidation=13, investigation=15,
                        leadership=17, medicae=17, persuasion=19, pilot=16,
                        psychic_mastery=19, scholar=21, stealth=19, survival=22,
                        tech=24, weapon_skill=23)
        npc = NPC(**npc_data())
        for name, value in expected.items():
            with self.subTest(name=name):
                self.assertEqual(npc.get_skill_dice_pool_value(name), value)
        npc.strength = npc.skills.athletics = 0
        self.assertEqual(npc.get_skill_dice_pool_value("athletics"), 0)

    def test_invalid_skill_names(self):
        # Verify invalid skill names raise the custom exception with the expected message.
        npc = NPC(**npc_data())
        for name in ("", "Athletics", "unknown", None, 123):
            with self.subTest(name=name), self.assertRaises(InvalidSkillNameException) as error:
                npc.get_skill_dice_pool_value(name)
            self.assertEqual(str(error.exception), f"Skill name {name} was invalid.")

    def test_invalid_skill_value_cannot_be_added(self):
        # Verify nonnumeric skill values raise TypeError during dice pool calculation.
        npc = NPC(**npc_data())
        for value in (None, "invalid"):
            npc.skills.athletics = value
            with self.subTest(value=value), self.assertRaises(TypeError):
                npc.get_skill_dice_pool_value("athletics")

    def test_from_dict_and_nested_abilities(self):
        # Verify NPC deserialization constructs nested Skills and Ability objects.
        payload = npc_payload()
        payload["abilities"] = [dict(ability_type="Action", name="Strike", text="Attack")]
        npc = NPC.from_dict(payload)
        expected = NPC(**npc_data(), abilities=[Ability("Action", "Strike", "Attack")])
        self.assertEqual(npc, expected)
        self.assertIsInstance(npc.skills, Skills)
        self.assertIsInstance(npc.abilities[0], Ability)

    def test_missing_deserialization_fields(self):
        # Verify omitting any required NPC payload field raises the matching KeyError.
        payload = npc_payload()
        for key in payload.keys() - {"picture", "id"}:
            data = dict(payload)
            del data[key]
            with self.subTest(key=key), self.assertRaises(KeyError) as error:
                NPC.from_dict(data)
            self.assertEqual(error.exception.args, (key,))

    def test_invalid_payload_and_nested_values(self):
        # Verify malformed NPC containers and nested skills, abilities, and weapons are rejected.
        for data in (None, 1, []):
            with self.subTest(data=data), self.assertRaises(TypeError):
                NPC.from_dict(data)
        for key, value, error in (("skills", {}, KeyError), ("skills", None, TypeError),
                                  ("abilities", [{}], KeyError), ("abilities", None, TypeError),
                                  ("weapons", [{}], KeyError), ("weapons", None, TypeError)):
            data = npc_payload()
            data[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(error):
                NPC.from_dict(data)

    def test_json_serializes_nested_models(self):
        # Verify NPC JSON preserves nested skills, abilities, weapons, and keywords.
        npc = NPC(**npc_data(), abilities=[Ability("Action", "Strike", "Attack")],
                  weapons=[Weapon(**weapon_data())], keywords=["Human"])
        self.assertEqual(json.loads(npc.to_json()), asdict(npc))

    def test_default_skills_can_be_constructed(self):
        # Verify an NPC can initialize skills when none are supplied;
        data = npc_data()
        del data["skills"]
        self.assertIsInstance(NPC(**data).skills, Skills)

    def test_default_skill_dice_pool(self):
        # Verify the default dice pool returns the default skill value;
        npc = NPC(**npc_data())
        self.assertEqual(npc.get_skill_dice_pool_value("default"), npc.skills.default)

    def test_from_dict_nested_weapon(self):
        # Verify NPC deserialization reconstructs nested weapons;
        payload = npc_payload()
        weapon = Weapon(**weapon_data())
        payload["weapons"] = [json.loads(weapon.to_json())]
        self.assertEqual(NPC.from_dict(payload).weapons, [weapon])

    def test_json_round_trip(self):
        # Verify NPC JSON can be read back into an equivalent NPC;
        npc = NPC(**npc_data())
        self.assertEqual(NPC.from_dict(json.loads(npc.to_json())), npc)


class ProtocolAndExceptionTests(unittest.TestCase):
    def test_has_group_contract(self):
        # Verify HasGroup declares a string group and model instances provide string groups.
        self.assertEqual(get_type_hints(HasGroup), {"group": str})
        for model in (NPC(**npc_data()), Weapon(**weapon_data())):
            self.assertIsInstance(model.group, str)

    def test_protocol_cannot_be_instantiated(self):
        # Verify the grouping protocol cannot be instantiated as a concrete class.
        with self.assertRaises(TypeError):
            HasGroup()

    def test_models_declare_group_contract(self):
        # Verify NPC and Weapon declare the string group required by HasGroup.
        # Check the declared structural contract without runtime protocol checks.
        for model_type in (NPC, Weapon):
            with self.subTest(model_type=model_type):
                self.assertIs(get_type_hints(model_type)["group"], str)

    def test_exception_message_and_args(self):
        # Verify the custom exception exposes the expected message and exception arguments.
        error = InvalidSkillNameException("missing")
        self.assertIsInstance(error, Exception)
        self.assertEqual(error.message, "Skill name missing was invalid.")
        self.assertEqual(error.args, (error.message,))


if __name__ == "__main__":
    unittest.main()
