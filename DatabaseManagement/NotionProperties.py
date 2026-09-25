from dataclasses import dataclass
from DatabaseManagement.RichText import RichText

@dataclass
class RichTextProperty:
    rich_text: list[RichText]
    type: str = "rich_text"

    def __init__(self, plain_text: str):
        self.rich_text = [RichText(plain_text)]

@dataclass
class TitleProperty:
    title: list[RichText]
    type: str = "title"

    def __init__(self, plain_text: str):
        self.title = [RichText(plain_text)]
