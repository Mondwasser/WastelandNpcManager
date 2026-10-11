from functools import partial
from typing import Any

from PySide6.QtCore import Slot, Qt, QSize
from PySide6.QtWidgets import QAbstractSpinBox, QLabel, QSpinBox, QGridLayout, QWidget, QComboBox, QLineEdit

from Data.NPC import NPC

npc_sizes = ["Tiny", "Small", "Avg", "Large", "Huge"]

class NpcAttributesView(QWidget):

    def __init__(self, model: NPC, fixed_width: int):
        super().__init__()

        self.model = model

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.setFixedWidth(fixed_width)
        self.layout.setSpacing(0)
        self.layout.setVerticalSpacing(0)
        self.layout.setHorizontalSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.shorthand_size = QSize(55,20)
        self.field_size = QSize(55,30)
        self.setFixedHeight(self.shorthand_size.height() + self.field_size.height() + 10)

        self.attributes = []
        self.attributes.append(self.add_attribute("S", self.model.strength, partial(self.attribute_changed, "strength")))
        self.attributes.append(self.add_attribute("T", self.model.toughness, partial(self.attribute_changed, "toughness")))
        self.attributes.append(self.add_attribute("A", self.model.agility, partial(self.attribute_changed, "agility")))
        self.attributes.append(self.add_attribute("I", self.model.initiative, partial(self.attribute_changed, "initiative")))
        self.attributes.append(self.add_attribute("Wil", self.model.willpower, partial(self.attribute_changed, "willpower")))
        self.attributes.append(self.add_attribute("Int", self.model.intelligence, partial(self.attribute_changed, "intelligence")))
        self.attributes.append(self.add_attribute("Fel", self.model.fellowship, partial(self.attribute_changed, "fellowship")))

    def add_attribute(self, shorthand:  str, attribute: int, slotFunction):

        column = self.layout.columnCount()

        label = QLabel(shorthand)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("QLabel { background-color: lightgrey; }")
        label.setFixedSize(self.shorthand_size)
        self.layout.addWidget(label, 0, column)

        field = QSpinBox(value=attribute, minimum=0, maximum=20)
        field.valueChanged.connect(slotFunction)
        field.setFixedSize(self.field_size)
        field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        field.setEnabled(False)
        field.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.layout.addWidget(field, 1, column)

        return field

    def attribute_changed(self, attribute_name: str, new_value: int):
        setattr(self.model, attribute_name, new_value)

    def setEditMode(self, enabled: bool):

        for attribute in self.attributes:
            attribute.setEnabled(enabled)
            if enabled:
                attribute.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
            else:
                attribute.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

class NpcSubAttributesView(QWidget):
    def __init__(self, model: NPC, fixed_width: int):
        super().__init__()

        self.model = model
        self.boxes = []

        self.setFixedWidth(fixed_width)

        grid_layout = QGridLayout()
        self.setLayout(grid_layout)
        grid_layout.setVerticalSpacing(0)
        grid_layout.setHorizontalSpacing(5)

        grid_layout.addWidget(self.create_label("Resolve"), 0, 0)
        grid_layout.addWidget(self.create_spin_box(self.model.resolve, partial(self.attribute_changed, "resolve")), 0, 1)

        grid_layout.addWidget(QLabel("Armor"), 0, 2)
        grid_layout.addWidget(self.create_spin_box(self.model.armor, partial(self.attribute_changed, "armor")), 0, 3)

        self.armour_name_box = QLineEdit(placeholderText="No Armor", text= model.armor_name)
        self.armour_name_box.setEnabled(False)
        self.armour_name_box.textEdited.connect(partial(self.attribute_changed, "armor_name"))
        grid_layout.addWidget(self.armour_name_box, 0, 4, 1 ,4)

        grid_layout.addWidget(QLabel("Defence"), 1, 0)
        grid_layout.addWidget(self.create_spin_box(self.model.defense,partial(self.attribute_changed, "defense")), 1, 1)

        grid_layout.addWidget(QLabel("Wounds"), 1, 2)
        grid_layout.addWidget(self.create_spin_box(self.model.wounds, partial(self.attribute_changed, "wounds")), 1, 3)

        grid_layout.addWidget(QLabel("Shock"), 1, 4)
        grid_layout.addWidget(self.create_spin_box(self.model.shock, partial(self.attribute_changed, "shock")), 1, 5)

        grid_layout.addWidget(QLabel("Conviction"), 2, 0)
        grid_layout.addWidget(self.create_spin_box(self.model.conviction, partial(self.attribute_changed, "conviction")), 2, 1)

        grid_layout.addWidget(QLabel("Resilience"), 2, 2)
        grid_layout.addWidget(self.create_spin_box(self.model.resilience, partial(self.attribute_changed, "resilience")), 2, 3)

        grid_layout.addWidget(QLabel("Speed"), 2, 4)
        grid_layout.addWidget(self.create_spin_box(self.model.speed, partial(self.attribute_changed, "speed")), 2, 5)

        grid_layout.addWidget(QLabel("Size"), 2, 6)
        self.size_box = QComboBox()
        self.size_box.addItems(npc_sizes)
        self.size_box.setEnabled(False)
        self.size_box.setEditable(False)
        self.size_box.currentIndexChanged.connect(partial(self.attribute_changed, "size"))

        if model.size in npc_sizes:
            self.size_box.setCurrentIndex(npc_sizes.index(model.size))
        else:
            self.size_box.setCurrentIndex(2)

        grid_layout.addWidget(self.size_box, 2, 7)

    def create_label(self, text: str):
        label = QLabel(text)
        return label

    def create_spin_box(self, value: int, slotFunction) -> QSpinBox:
        box = QSpinBox(value=value, minimum=0, maximum=20)
        box.valueChanged.connect(slotFunction)
        box.setEnabled(False)
        box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.boxes.append(box)

        return box

    def setEditMode(self, enabled: bool):

        self.armour_name_box.setEnabled(enabled)
        self.size_box.setEnabled(enabled)

        for box in self.boxes:
            box.setEnabled(enabled)
            if enabled:
                box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
            else:
                box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

    def attribute_changed(self, attribute_name: str, new_value: Any):
        setattr(self.model, attribute_name, new_value)