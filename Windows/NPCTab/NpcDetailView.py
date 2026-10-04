from PySide6.QtCore import Qt, QSize, Slot, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton

from Data.NPC import NPC
from Windows.NPCTab.NpcAbilityView import NpcAbilityView
from Windows.NPCTab.NpcAttributeView import NpcAttributesView, NpcSubAttributesView
from Windows.NPCTab.NpcSkillView import NpcSkillView
from Windows.NPCTab.NpcWeaponView import NpcWeaponView


class NpcDetailView(QWidget):

    picture_size = QSize(150,200)
    minimum_right_side_width = 400

    #Signals
    nameChanged = Signal(str)

    def __init__(self, model: NPC, fixed_width: int):
        super(NpcDetailView, self).__init__()

        fixed_width_right = max(fixed_width - self.picture_size.width(), self.minimum_right_side_width)

        self.model = model

        self.backup_model = None
        self.is_editing = False
        self.view_parts = []

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        #Top row containing name and edit button
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        name_label = QLabel("Name: ")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("QLabel { color: grey; }")
        top_layout.addWidget(name_label)

        self.name_field = QLineEdit(placeholderText="Character needs a name", text=model.name, readOnly=True)
        self.name_field.textEdited.connect(self.name_changed)
        top_layout.addWidget(self.name_field)

        self.edit_and_save_btn = QPushButton("Edit")
        button_layout = QHBoxLayout()
        self.edit_and_save_btn.clicked.connect(self.edit_save_btn_clicked)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        button_layout.addWidget(self.edit_and_save_btn)
        top_layout.addLayout(button_layout)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.hide()
        self.cancel_btn.clicked.connect(self.cancel_btn_clicked)
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        button_layout.addWidget(self.cancel_btn)
        top_layout.addLayout(button_layout)

        lower_layout = QHBoxLayout()
        main_layout.addLayout(lower_layout)

        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        lower_layout.addWidget(left_widget)
        left_widget.setFixedWidth(self.picture_size.width())

        picture_label = QLabel()
        picture_label.setFixedSize(self.picture_size)
        picture_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        if model.picture is not None:
            picture_label.setPixmap(model.picture.scaled(self.picture_size, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            picture_label.setPixmap(QPixmap("Media/NoImage.jpg").scaled(self.picture_size, Qt.AspectRatioMode.KeepAspectRatio))

        left_layout.addWidget(picture_label)

        left_layout.addWidget(QLabel("Faction:"))
        faction_label = QLabel(model.group)
        faction_label.setStyleSheet("QLabel { color: grey; }")
        left_layout.addWidget(faction_label)

        left_layout.addWidget(QLabel("Faction Tags:"))
        faction_label = QLabel(", ".join(model.faction_keywords))
        faction_label.setStyleSheet("QLabel { color: grey; }")
        left_layout.addWidget(faction_label)

        left_layout.addWidget(QLabel("Keywords:"))
        faction_label = QLabel(", ".join(model.keywords))
        faction_label.setStyleSheet("QLabel { color: grey; }")
        left_layout.addWidget(faction_label)

        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        lower_layout.addLayout(right_layout)

        npc_attribute_view = NpcAttributesView(model, fixed_width_right)
        self.view_parts.append(npc_attribute_view)
        right_layout.addWidget(npc_attribute_view)

        npc_subattribute_view = NpcSubAttributesView(model, fixed_width_right)
        self.view_parts.append(npc_subattribute_view)
        right_layout.addWidget(npc_subattribute_view)

        npc_skill_view = NpcSkillView(model, fixed_width_right)
        self.view_parts.append(npc_skill_view)
        right_layout.addWidget(npc_skill_view)

        npc_weapon_view = NpcWeaponView(model, fixed_width_right)
        self.view_parts.append(npc_weapon_view)
        right_layout.addWidget(npc_weapon_view)

        npc_ability_view = NpcAbilityView(model, fixed_width_right)
        self.view_parts.append(npc_ability_view)
        right_layout.addWidget(npc_ability_view)

    def setEditMode(self, enable: bool):
        if enable:
            self.is_editing = True
            self.edit_and_save_btn.setText("Save")
            self.cancel_btn.show()
            self.name_field.setReadOnly(False)
        else:
            self.is_editing = False
            self.edit_and_save_btn.setText("Edit")
            self.cancel_btn.hide()
            self.name_field.setReadOnly(True)

        for view_part in self.view_parts:
            view_part.setEditMode(enable)

    @Slot()
    def edit_save_btn_clicked(self):
        if self.is_editing:
            # Saving
            #TODO Checks e.g. Name not empty
            #TODO trigger Popup if was changed
            self.setEditMode(False)
        else:
            self.backup_model = self.model
            self.setEditMode(True)

    @Slot()
    def cancel_btn_clicked(self):
        #TODO trigger Popup if was changed
        self.setEditMode(False)
        pass

    @Slot(str)
    def name_changed(self, new_name):
        self.model.name = new_name
        self.nameChanged.emit(new_name)