import math

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from Data.NPC import NPC
from Windows.NPCTab.NpcDetailSubBaseView import NpcDetailSubBaseView

class NpcSkillView(NpcDetailSubBaseView):

    def __init__(self, model: NPC, fixed_width: int):

        super().__init__(model, "Skills", fixed_width, self.edit_skills)
        self.skills_label = QLabel()
        self.skills_label.setTextFormat(Qt.TextFormat.RichText)
        self.skills_label.setWordWrap(True)
        self.skills_label.setText(self.generate_skill_text())

        self.main_layout.addWidget(self.skills_label)

    def edit_skills(self):
        pass

    def setEditMode(self, enable: bool) -> None:
        super().setEditMode(enable)

    def generate_skill_text(self) -> str:
        skill_list = [ f"<b>Default: {self.model.skills.default}</b>"]

        awareness_value = self.model.get_skill_dice_pool_value("awareness")
        skill_list.append("Awareness: " + str(awareness_value) + " (Passive " + str(math.floor(awareness_value * 0.5)) + ")")

        for key in set(self.model.skills.__dict__) - { "default", "awareness"}:
            if getattr(self.model.skills,key) != 0:
                skill_list.append(key.title().replace('_',' ') + ": " + str(self.model.get_skill_dice_pool_value(key)))

        return ", ".join(skill_list)