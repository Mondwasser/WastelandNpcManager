from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton

from Data.NPC import NPC

class NpcDetailSubBaseView(QWidget):
    title_height = 35
    button_width = 100

    def __init__(self, model: NPC, titel: str, fixed_width: int, edit_fnc: Callable):
        super().__init__()

        self.model = model
        self.setFixedWidth(fixed_width)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        title_container = QWidget()
        title_container.setLayout(title_layout)
        title_container.setStyleSheet("background-color: lightgrey;")
        title_container.setFixedHeight(self.title_height)
        self.main_layout.addWidget(title_container)

        skill_label = QLabel(f"<b>{titel}</b>")
        skill_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(skill_label)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setFixedWidth(self.button_width)
        self.edit_btn.hide()
        self.edit_btn.clicked.connect(edit_fnc)
        title_layout.addWidget(self.edit_btn)

    def setEditMode(self, enable: bool):
        if enable:
            self.edit_btn.show()
        else:
            self.edit_btn.hide()