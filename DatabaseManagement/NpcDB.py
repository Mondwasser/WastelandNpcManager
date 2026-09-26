from dataclasses import asdict
from Data.NPC import NPC
from DatabaseManagement.Notion.NotionClient import NotionClient
from DatabaseManagement.Notion.NotionProperties import TitleProperty, RichTextProperty
import json

class NpcDB:
    """Handles storing and retrieving NPCs from Notion"""
    def __init__(self):
        self.client = NotionClient()
        self.db_id = "3e77e8e3bc9980c29effd705e2457f7a"

    def get_all(self):
        """Gets all npcs stored in Notion"""
        data = self.client.get_pages(self.db_id)
        npcs = []

        for page in data:
            properties = page["properties"]["Npc"]["rich_text"][0]["plain_text"]
            new_npc = NPC.from_dict(json.loads(properties))
            new_npc.id = page["id"]
            npcs.append(new_npc)

        return npcs

    def add_new(self, npc: NPC):
        """Adds a new npc to Notion"""
        data = {
                "Name" : asdict(TitleProperty(npc.name)),
                "Npc" : asdict(RichTextProperty(npc.to_json()))
               }

        self.client.add_page(self.db_id, data)

    def update(self, npc: NPC):
        """Updates npc on Notion"""
        data = {
            "Name": asdict(TitleProperty(npc.name)),
            "Npc": asdict(RichTextProperty(npc.to_json()))
        }
        self.client.update_page(npc.id, data)

    def delete(self, npc: NPC):
        """Deletes a npc from Notion"""
        self.client.delete_page(npc.id)