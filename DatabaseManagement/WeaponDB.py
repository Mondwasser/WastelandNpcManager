from dataclasses import asdict
from Data.Weapon import Weapon
from DatabaseManagement.NotionClient import NotionClient
from DatabaseManagement.NotionProperties import TitleProperty, RichTextProperty
import json

class WeaponDB:
    """Handles storing and retrieving weapons from Notion"""
    def __init__(self):
        self.client = NotionClient()
        self.db_id = "3e67e8e3bc99800ca62ec501c9b02016"

    def get_all_weapons(self):
        """Gets all weapons stored in Notion"""
        data = self.client.get_pages(self.db_id)
        weapons = []

        for page in data:
            properties = page["properties"]["weapon"]["rich_text"][0]["plain_text"]
            weapon_string = json.loads(properties)
            new_weapon = Weapon.from_dict(weapon_string)
            new_weapon.id = page["id"]
            weapons.append(new_weapon)

        return weapons

    def add_new_weapon(self, weapon: Weapon):
        """Adds a new weapon to Notion"""
        data = {
                "Name" : asdict(TitleProperty(weapon.name)),
                "weapon" : asdict(RichTextProperty(weapon.to_json()))
               }

        self.client.add_page(self.db_id, data)