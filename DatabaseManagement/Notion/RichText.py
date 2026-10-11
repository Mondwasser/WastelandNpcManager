from dataclasses import dataclass, field

@dataclass
class Text:
    """Represents a Text field in Notion"""
    content: str
    link: str = None

@dataclass()
class Annotations:
    """Represents a Annotations field in Notion"""
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: bool = "default"

@dataclass
class RichText:
    """Represents a RichText field in Notion"""

    text: Text = field(default_factory=Text)
    annotations: Annotations = field(default_factory=Annotations)
    type: str = field(default= "text", init=False)
    plain_text: str = ""
    href: str = None

    def __init__(self, plainText: str):
        self.text = Text(content= plainText)
        self.plainText = plainText
        self.annotations = Annotations()
        self.type = "text"
        self.href = "null"