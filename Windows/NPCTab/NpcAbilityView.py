from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from Data.Ability import Ability
from Data.NPC import NPC
from Windows.CustomButtons import DeleteButton
from Windows.NPCTab.NpcDetailSubBaseView import NpcDetailSubBaseView

class AbilityDetailView(QWidget):
    """View displaying a single ability"""

    label_fixed_height = 20
    remove_ability_clicked = Signal(object)

    def __init__(self, model: Ability, fixed_width: int):
        super().__init__()

        self.setFixedWidth(fixed_width)
        self.model = model

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setSpacing(0)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(5)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.main_layout.addLayout(title_layout)

        self.title_label = QLabel(f"<b>{self.model.ability_type.upper()}: {self.model.name}</b>")
        self.title_label.setTextFormat(Qt.TextFormat.RichText)
        self.title_label.setFixedHeight(self.label_fixed_height)

        title_layout.addWidget(self.title_label)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self.edit_ability)
        self.edit_btn.hide()

        title_layout.addWidget(self.edit_btn)

        self.remove_btn = DeleteButton()
        self.remove_btn.clicked.connect(self.remove_ability)
        self.remove_btn.hide()

        title_layout.addWidget(self.remove_btn)

        self.attributes_label = QLabel()
        self.attributes_label.setWordWrap(True)
        self.attributes_label.setText(self.model.text)

        self.main_layout.addWidget(self.attributes_label)

    def remove_ability(self):
        #TODO Add popup
        self.remove_ability_clicked.emit(self)

    def edit_ability(self):
        pass

    def setEditMode(self, enable: bool, /) -> None:

        if enable:
            self.remove_btn.show()
            self.edit_btn.show()
        else:
            self.remove_btn.hide()
            self.edit_btn.hide()

class NpcAbilityView(NpcDetailSubBaseView):
    """View displaying a NPCs abilities and handling adding, and removal of abilities"""

    def __init__(self, model: NPC, fixed_width: int):
        super().__init__(model, "Abilities", fixed_width, self.add_ability_clicked)

        self.edit_btn.setText("Add Ability")

        self.abilities = []
        for ability in model.abilities:
            new_ability = AbilityDetailView(ability, fixed_width)
            new_ability.remove_ability_clicked.connect(self.remove_ability_clicked)
            self.main_layout.addWidget(new_ability)
            self.abilities.append(new_ability)

    def setEditMode(self, enable: bool) -> None:
        """Enables/disables ability editing mode"""
        super().setEditMode(enable)

        for ability in self.abilities:
            ability.setEditMode(enable)

    def add_ability_clicked(self) -> None:
        """Adds an ability to the ability list"""
        pass

    @Slot(AbilityDetailView)
    def remove_ability_clicked(self, ability_view: AbilityDetailView) -> None:
        """Removes an ability from the ability list"""
        ability_view.remove_ability_clicked.connect(self.remove_ability_clicked)
        self.main_layout.removeWidget(ability_view)
        self.abilities.remove(ability_view)
        self.model.abilities.remove(ability_view.model)
        ability_view.deleteLater()

