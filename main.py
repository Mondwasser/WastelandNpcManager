import os
from DatabaseManagement.NotionClient import NotionClient
import json

def test_client():
    client = NotionClient()
    data = client.get_pages("1e47e8e3bc9980acbd89e8b7e526a359")
    print(len(data))

def test_load_weapons():
    with open("Data/WeaponTraits.json", "r") as json_file:
        data = json.load(json_file)
        return data

print("Running...")
data = test_load_weapons()
