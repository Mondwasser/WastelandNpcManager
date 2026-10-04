from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from Data.NPC import NPC
from Data.Weapon import Weapon
from Windows.CustomButtons import DeleteButton
from Windows.NPCTab.NpcDetailSubBaseView import NpcDetailSubBaseView

class WeaponDetailView(QWidget):

    remove_weapon_clicked = Signal(object)
    label_fixed_height = 20

    def __init__(self, model: Weapon, wielder_strength: int, fixed_width: int):
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

        self.title_label = QLabel(f"<b>{self.model.name}:</b>")
        self.title_label.setTextFormat(Qt.TextFormat.RichText)
        self.title_label.setFixedHeight(self.label_fixed_height)

        title_layout.addWidget(self.title_label)

        self.remove_weapon_btn = DeleteButton()
        self.remove_weapon_btn.clicked.connect(self.remove_weapon)
        self.remove_weapon_btn.hide()

        title_layout.addWidget(self.remove_weapon_btn)

        self.attributes_label = QLabel()
        self.attributes_label.setTextFormat(Qt.TextFormat.RichText)
        self.attributes_label.setWordWrap(True)
        self.attributes_label.setFixedHeight(self.label_fixed_height)
        self.attributes_label.setText(WeaponTextGenerator.generate_weapon_attribute_text(model, wielder_strength))

        self.main_layout.addWidget(self.attributes_label)

    def setEditMode(self, enable: bool) -> None:
        if enable:
            self.remove_weapon_btn.show()
        else:
            self.remove_weapon_btn.hide()

    def remove_weapon(self):
        self.remove_weapon_clicked.emit(self)

class NpcWeaponView(NpcDetailSubBaseView):

    def __init__(self, model: NPC, fixed_width: int):
        super().__init__(model, "Weapons", fixed_width, self.add_weapon_clicked)

        self.edit_btn.setText("Add Weapons")

        self.weapons= []
        for weapon in model.weapons:
            new_weapon = WeaponDetailView(weapon, model.strength, fixed_width)
            new_weapon.remove_weapon_clicked.connect(self.remove_weapon_clicked)
            self.weapons.append(new_weapon)
            self.main_layout.addWidget(new_weapon)

    def setEditMode(self, enable: bool) -> None:

        super().setEditMode(enable)

        for weapon in self.weapons:
            weapon.setEditMode(enable)

    def add_weapon_clicked(self):
        pass

    @Slot(WeaponDetailView)
    def remove_weapon_clicked(self, weapon_view: WeaponDetailView):
        weapon_view.remove_weapon_clicked.disconnect(self.remove_weapon_clicked)
        self.main_layout.removeWidget(weapon_view)
        self.weapons.remove(weapon_view)
        self.model.weapons.remove(weapon_view.model)
        weapon_view.deleteLater()

class WeaponTextGenerator():

    @staticmethod
    def generate_weapon_attribute_text(weapon: Weapon, wielder_strength: int) -> str:

        weapon_damage = weapon.damage + weapon.is_strength_based * wielder_strength
        weapon_attributes = [f"{weapon_damage} + {str(weapon.extra_dice)} ED"]

        if weapon.armor_penetration != 0:
            weapon_attributes.append(f"AP {weapon.armor_penetration}")

        weapon_attributes.append(WeaponTextGenerator.get_range_text(weapon, wielder_strength))

        weapon_attributes.append(", ".join(weapon.traits))

        return " / ".join(weapon_attributes)

    @staticmethod
    def get_range_text(weapon: Weapon, wielder_strength: int) -> str:

        if weapon.is_strength_based:
            if weapon.range.strength_multiplier_for_throw == 0:
                return f"Range {weapon.range.melee_range}"
            else:
                return f"Range {weapon.range.melee_range}m or Thrown({wielder_strength * weapon.range.strength_multiplier_for_throw})"
        else:
            return f"Range {weapon.range.short}-{weapon.range.medium}-{weapon.range.long}"