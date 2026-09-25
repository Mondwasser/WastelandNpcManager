import os
from dataclasses import asdict

from Data.Weapon import ShootingRange, ThrowingRange, Range, Weapon
from DatabaseManagement.NotionClient import NotionClient
import json

from TestData.ExampleWeapons import exampleGun, exampleMelee


def test_client():
    client = NotionClient()
    data = client.get_pages("1e47e8e3bc9980acbd89e8b7e526a359")
    print(len(data))

def test_load_weapons():
    with open("Data/WeaponTraits.json", "r") as json_file:
        data = json.load(json_file)
        return data

def save_weapons():
    data = json.dumps(asdict(exampleMelee))
    print(data)
    restoredData = Weapon.from_dict(json.loads(data))
    print(restoredData)

def test_dicting():
    rangeShoot = ShootingRange(12,24,36)
    rangeThrow = ThrowingRange(4)
    print(f"Shooting Object: {rangeShoot}")
    print(f"Throwing Object: {rangeThrow}")

    dict_of_range = rangeShoot.to_dict()
    dict_of_throw = rangeThrow.to_dict()

    print(f"Shooting dict: {dict_of_range}")
    print(f"Throwing dict: {dict_of_throw}")

    restored_shoot = Range.cls_from_dict(dict_of_range)
    restored_throw = Range.cls_from_dict(dict_of_throw)

    print(f"Shooting Object: {restored_shoot}")
    print(f"Throwing Object: {restored_throw}")

print("Running...")
data = save_weapons()
