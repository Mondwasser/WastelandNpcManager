import os
from dataclasses import asdict

from Data.Weapon import ShootingRange, ThrowingRange, Range, Weapon
from DatabaseManagement.NotionClient import NotionClient
import json

from DatabaseManagement.NotionProperties import TitleProperty, RichTextProperty
from DatabaseManagement.WeaponDB import WeaponDB
from TestData import ExampleWeapons
from TestData.ExampleWeapons import exampleGun, exampleMelee

db_id_bestiary = "1e47e8e3bc9980acbd89e8b7e526a359"
db_id_weapons = "3e67e8e3bc99800ca62ec501c9b02016"
page_id_first_citizen = "1e97e8e3bc99814a8882d2f4531da8db"

def test_client():
    client = NotionClient()
    data = client.get_pages(db_id_bestiary)
    print(len(data))

def test_get_page():
    client = NotionClient()
    data = client.get_page(db_id_bestiary, page_id_first_citizen)
    print(len(data))

def test_add_weapon():
    client = WeaponDB()
    client.add_new_weapon(exampleMelee)

def test_load_weapons():
    client = WeaponDB()
    data = client.get_all_weapons()

    print(f"{len(data)} weapons found")

def test_load_weapon_traits():
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

client = WeaponDB()
data = client.get_all_weapons()
print(f"{len(data)} weapons found")

client.delete_weapon(data[0])




