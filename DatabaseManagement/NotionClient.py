import json
import os
import requests


class NotionClient:
    """Client for Notion API"""

    def __init__(self):
        self.headers = {
            "Authorization": "Bearer " + os.environ['NOTION_TOKEN'],
            "Content-Type": "application/json",
            "Notion-Version": "2022-02-22",
        }

    def get_pages(self, database_id, num_pages=None):
        """ If num_pages is None, get all pages, otherwise just the defined number. """
        url = f"https://api.notion.com/v1/databases/{database_id}/query"

        get_all = num_pages is None
        page_size = 100 if get_all else num_pages

        payload = {"page_size": page_size}
        response = requests.post(url, json=payload, headers=self.headers)

        data = response.json()

        results = data["results"]
        while data["has_more"] and get_all:
            payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
            url = f"https://api.notion.com/v1/databases/{database_id}/query"
            response = requests.post(url, json=payload, headers=self.headers)
            data = response.json()
            results.extend(data["results"])

        return results

    def get_page(self, database_id, page_id):
        url = f"https://api.notion.com/v1/pages/{page_id}"
        response = requests.get(url, headers=self.headers)

        data = response.json()
        return data

    def add_page(self, database_id, data: dict):
        url = "https://api.notion.com/v1/pages"

        payload = {
            "parent": {
                "database_id": database_id,
                "type": "database_id"
            },
            "properties": data
        }

        response = requests.post(url, json=payload, headers=self.headers)

        json_response = response.json()

        if (json_response["object"] == "error"):
            print(json_response["code"])
            print("\n")
            print(json_response["message"])

        return json_response