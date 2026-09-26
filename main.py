from dataclasses import asdict

from Data.Ability import Ability
from Data.NPC import NPC
from Data.Weapon import ShootingRange, ThrowingRange, Range, Weapon
from DatabaseManagement import NpcDB
from DatabaseManagement.Notion.NotionClient import NotionClient
import json

from DatabaseManagement.WeaponDB import WeaponDB
from TestData import ExampleNPCs
from TestData.ExampleWeapons import exampleMelee

db_id_bestiary = "1e47e8e3bc9980acbd89e8b7e526a359"
db_id_weapons = "3e67e8e3bc99800ca62ec501c9b02016"
page_id_first_citizen = "1e97e8e3bc99814a8882d2f4531da8db"

def test_client():
    client = NotionClient()
    data = client.get_pages(db_id_bestiary)
    print(len(data))


print("Running...")

data = ExampleNPCs.KER

client = NpcDB.NpcDB()

new_data = client.get_all()

client.delete(new_data[0])



