"""Offscreen Qt tests; no GUI windows, database credentials, or network required."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PySide6.QtCore import QCoreApplication, QEvent, Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QApplication, QAbstractSpinBox, QLabel, QListWidget

from Data.Ability import Ability
from Data.NPC import NPC
from Data.Skills import Skills
from Data.Weapon import MeleeRange, ShootingRange, Weapon
from Windows.CustomButtons import DeleteButton
from Windows.TabListView import GroupItem, TabListView, TabTreeModel, TreeItem
from Windows.NPCTab.NpcAbilityView import AbilityDetailView, NpcAbilityView
from Windows.NPCTab.NpcAttributeView import NpcAttributesView, NpcSubAttributesView, npc_sizes
from Windows.NPCTab.NpcDetailSubBaseView import NpcDetailSubBaseView
from Windows.NPCTab.NpcDetailView import NpcDetailView
from Windows.NPCTab.NpcSkillView import NpcSkillView
from Windows.NPCTab.NpcTab import NpcTab
from Windows.NPCTab.NpcWeaponView import NpcWeaponView, WeaponDetailView, WeaponTextGenerator
from tests.test_data import npc_data, weapon_data


def make_npc():
    data = npc_data()
    data["size"] = "Avg"
    return NPC(**data)


class QtTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Keep one application alive for the entire suite, without visible windows.
        cls.environment = patch.dict(os.environ, {"QT_QPA_PLATFORM": "offscreen"})
        cls.environment.start()
        cls.addClassCleanup(cls.environment.stop)
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.widgets = []
        guard = patch("requests.sessions.Session.request",
                      side_effect=AssertionError("Real HTTP calls are forbidden in window tests"))
        guard.start()
        self.addCleanup(guard.stop)

    def own(self, widget):
        self.widgets.append(widget)
        return widget

    def tearDown(self):
        for widget in reversed(self.widgets):
            widget.close()
            widget.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        self.app.processEvents()


class ListViewTests(QtTestCase):
    def make_list(self):
        models = [SimpleNamespace(name="Guard", group="Imperium"),
                  SimpleNamespace(name="Medic", group="Imperium"),
                  SimpleNamespace(name="Raider", group="Chaos")]
        return self.own(TabListView("NPCs", TabTreeModel(models))), models

    def test_grouping_preserves_order(self):
        # Verify repeated groups combine their models while preserving group and item order.
        data = [SimpleNamespace(group="A"), SimpleNamespace(group="B"), SimpleNamespace(group="A")]
        model = TabTreeModel(data)
        self.assertIs(model.data, data)
        self.assertEqual(list(model.grouped_data), ["A", "B"])
        self.assertEqual(model.grouped_data, {"A": [data[0], data[2]], "B": [data[1]]})

    def test_empty_and_invalid_grouping(self):
        # Verify empty input creates no groups and invalid models or unhashable groups are rejected.
        self.assertEqual(TabTreeModel([]).grouped_data, {})
        for data, error in ((None, TypeError), ([object()], AttributeError),
                            ([SimpleNamespace(group=[])], TypeError)):
            with self.subTest(data=data), self.assertRaises(error):
                TabTreeModel(data)

    def test_group_header_and_children(self):
        # Verify group headers have the expected text, background, flags, and appended child list.
        group = GroupItem("Imperium")
        child = TreeItem(SimpleNamespace(name="Guard"))
        group.append(child)
        self.assertEqual(group.text(), "Imperium")
        self.assertEqual(group.background().color(), QColor("lightgrey"))
        self.assertFalse(group.flags() & Qt.ItemFlag.ItemIsSelectable)
        self.assertEqual(group.childItems, [child])

    def test_tree_item_name_refresh(self):
        # Verify tree item labels use indentation and refresh after the model name changes.
        model = SimpleNamespace(name="Guard")
        item = TreeItem(model)
        self.assertIs(item.model, model)
        self.assertEqual(item.text(), "  Guard")
        model.name = "Medic"
        item.updateTextWithModelName()
        self.assertEqual(item.text(), "  Medic")

    def test_invalid_tree_item_model(self):
        # Verify missing names and non-string names cannot construct a tree item.
        for model, error in ((object(), AttributeError), (SimpleNamespace(name=None), TypeError)):
            with self.subTest(model=model), self.assertRaises(error):
                TreeItem(model)

    def test_list_contents(self):
        # Verify each group header and model appears once in the expected list order.
        view, models = self.make_list()
        self.assertEqual([view.list_widget.item(i).text() for i in range(view.list_widget.count())],
                         ["Imperium", "  Guard", "  Medic", "Chaos", "  Raider"])
        self.assertEqual(view.group_items[0].childItems[0].model, models[0])

    def test_search_filters_groups_and_names(self):
        # Verify trimmed case-insensitive searches match groups or names and hide unmatched headers.
        view, _ = self.make_list()
        for search, visible in (("  IMPERIUM  ", [True, True, True, False, False]),
                                ("medic", [True, False, True, False, False]),
                                ("missing", [False] * 5), ("", [True] * 5)):
            with self.subTest(search=search):
                view.update_display(search)
                self.assertEqual([not view.list_widget.item(i).isHidden() for i in range(5)], visible)

    def test_selection_signal(self):
        # Verify selecting a model emits that model while headers and cleared selections emit nothing.
        view, models = self.make_list()
        selected = Mock()
        view.selectedItemChanged.connect(selected)
        view.list_widget.setCurrentRow(1)
        selected.assert_called_once_with(models[0])
        selected.reset_mock()
        view.list_widget.setCurrentRow(0)
        view.selection_changed()
        view.list_widget.setCurrentRow(-1)
        view.selection_changed()
        selected.assert_not_called()

    def test_selected_name_update(self):
        # Verify a model name change refreshes the currently selected tree item's text.
        view, models = self.make_list()
        view.list_widget.setCurrentRow(1)
        models[0].name = "Veteran"
        view.tree_item_name_changed("Veteran")
        self.assertEqual(view.list_widget.currentItem().text(), "  Veteran")

    def test_all_children_hidden_semantics(self):
        # Verify the method reports true when all children are hidden;
        owner = self.own(QListWidget())
        group = GroupItem("Group")
        child = TreeItem(SimpleNamespace(name="Child"))
        owner.addItem(group)
        owner.addItem(child)
        group.append(child)
        child.setHidden(True)
        self.assertTrue(group.all_children_hidden())


class ButtonAndBaseViewTests(QtTestCase):
    def test_delete_button_size_icon_and_click(self):
        # Verify default/custom delete button sizes, rounded styling, icon, and clicked signal.
        for size in (16, 24):
            with self.subTest(size=size):
                button = self.own(DeleteButton() if size == 16 else DeleteButton(size))
                self.assertEqual((button.width(), button.height()), (size, size))
                self.assertFalse(button.icon().isNull())
                self.assertIn(f"border-radius: {size // 2}px", button.styleSheet())
                clicked = Mock()
                button.clicked.connect(clicked)
                button.click()
                clicked.assert_called_once()

    def test_base_view_title_and_callback(self):
        # Verify the base subview displays its title, retains its model, and calls its edit callback.
        model, callback = make_npc(), Mock()
        view = self.own(NpcDetailSubBaseView(model, "Section", 500, callback))
        self.assertIs(view.model, model)
        self.assertEqual(view.width(), 500)
        self.assertIn("<b>Section</b>", [label.text() for label in view.findChildren(QLabel)])
        self.assertTrue(view.edit_btn.isHidden())
        view.setEditMode(True)
        self.assertFalse(view.edit_btn.isHidden())
        view.edit_btn.click()
        callback.assert_called_once()
        view.setEditMode(False)
        self.assertTrue(view.edit_btn.isHidden())


class AttributeViewTests(QtTestCase):
    def test_primary_values_and_edit_mode(self):
        # Verify all seven attribute values display read-only and editing toggles their spin controls.
        model = make_npc()
        view = self.own(NpcAttributesView(model, 500))
        names = ["strength", "toughness", "agility", "initiative", "willpower", "intelligence", "fellowship"]
        self.assertEqual([box.value() for box in view.attributes], [getattr(model, n) for n in names])
        for enabled in (True, False):
            view.setEditMode(enabled)
            for box in view.attributes:
                self.assertEqual(box.isEnabled(), enabled)
                expected = QAbstractSpinBox.ButtonSymbols.UpDownArrows if enabled else QAbstractSpinBox.ButtonSymbols.NoButtons
                self.assertEqual(box.buttonSymbols(), expected)

    def test_primary_changes_and_bounds(self):
        # Verify every attribute signal updates its model field and values are clamped to 0 through 20.
        model = make_npc()
        view = self.own(NpcAttributesView(model, 500))
        names = ["strength", "toughness", "agility", "initiative", "willpower", "intelligence", "fellowship"]
        for name, box in zip(names, view.attributes):
            for requested, expected in ((12, 12), (-1, 0), (21, 20)):
                with self.subTest(name=name, requested=requested):
                    box.setValue(requested)
                    self.assertEqual(getattr(model, name), expected)

    def test_secondary_values_changes_and_edit_mode(self):
        # Verify secondary stats display their model values, update on changes, and toggle editing together.
        model = make_npc()
        view = self.own(NpcSubAttributesView(model, 500))
        names = ["resolve", "armor", "defense", "wounds", "shock", "conviction", "resilience", "speed"]
        self.assertEqual([box.value() for box in view.boxes], [getattr(model, n) for n in names])
        for name, box in zip(names, view.boxes):
            box.setValue(13)
            self.assertEqual(getattr(model, name), 13)
        view.armour_name_box.textEdited.emit("Power Armor")
        self.assertEqual(model.armor_name, "Power Armor")
        for enabled in (True, False):
            view.setEditMode(enabled)
            for box in [*view.boxes, view.armour_name_box, view.size_box]:
                self.assertEqual(box.isEnabled(), enabled)

    def test_secondary_bounds(self):
        # Verify all secondary stat spin boxes clamp invalid values to their allowed bounds.
        view = self.own(NpcSubAttributesView(make_npc(), 500))
        for box in view.boxes:
            box.setValue(-1)
            self.assertEqual(box.value(), 0)
            box.setValue(100)
            self.assertEqual(box.value(), 20)

    def test_size_options_and_unknown_fallback(self):
        # Verify the size menu contains the declared sizes and unknown input displays Avg.
        model = make_npc()
        model.size = "Unknown"
        view = self.own(NpcSubAttributesView(model, 500))
        self.assertEqual([view.size_box.itemText(i) for i in range(view.size_box.count())], npc_sizes)
        self.assertEqual(view.size_box.currentText(), "Avg")

    def test_size_change_preserves_string(self):
        # Verify selecting a size stores its text in the NPC
        model = make_npc()
        view = self.own(NpcSubAttributesView(model, 500))
        view.size_box.setCurrentIndex(4)
        self.assertEqual(model.size, "Huge")


class SkillViewTests(QtTestCase):
    def test_skill_text_default_awareness_and_named_skills(self):
        # Verify default, awareness/passive, and nonzero named skills render with their dice pools.
        model = make_npc()
        model.skills = Skills(default=4, awareness=2, psychic_mastery=3)
        view = self.own(NpcSkillView(model, 500))
        text = view.generate_skill_text()
        self.assertIn("<b>Default: 4</b>", text)
        self.assertIn("Awareness: 9 (Passive 4)", text)
        self.assertIn("Psychic Mastery: 9", text)
        self.assertNotIn("Athletics", text)
        self.assertEqual(view.skills_label.text(), text)
        self.assertTrue(view.skills_label.wordWrap())

    def test_skill_edit_mode_and_placeholder(self):
        # Verify the skill edit button follows edit mode and the unimplemented editor leaves skills unchanged.
        model = make_npc()
        view = self.own(NpcSkillView(model, 500))
        original = dict(vars(model.skills))
        view.setEditMode(True)
        self.assertFalse(view.edit_btn.isHidden())
        view.edit_btn.click()
        self.assertEqual(vars(model.skills), original)
        view.setEditMode(False)
        self.assertTrue(view.edit_btn.isHidden())

    def test_invalid_skill_value(self):
        # Verify invalid skill values fail during text generation rather than producing a dice pool.
        model = make_npc()
        model.skills.awareness = None
        with self.assertRaises(TypeError):
            NpcSkillView(model, 500)


class WeaponTextTests(unittest.TestCase):
    def test_shooting_text(self):
        # Verify shooting damage ignores wielder strength and includes AP, range, and traits.
        weapon = Weapon(**weapon_data())
        self.assertEqual(WeaponTextGenerator.generate_weapon_attribute_text(weapon, 10),
                         "7 + 1 ED / AP -1 / Range 12-24-36 / Reliable")

    def test_melee_and_throwing_text(self):
        # Verify melee damage adds strength and thrown range multiplies the wielder's strength.
        data = weapon_data()
        data.update(is_melee=True, is_strength_based=True, range=MeleeRange(0, 2), armor_penetration=0)
        weapon = Weapon(**data)
        self.assertEqual(WeaponTextGenerator.generate_weapon_attribute_text(weapon, 3),
                         "10 + 1 ED / Range 2 / Reliable")
        weapon.range = MeleeRange(2, 1)
        self.assertEqual(WeaponTextGenerator.get_range_text(weapon, 3), "Range 1m or Thrown(6)")

    def test_multiple_and_empty_traits(self):
        # Verify traits are comma separated and an empty trait list retains the current trailing separator.
        weapon = Weapon(**weapon_data())
        weapon.traits = ["Reliable", "Rapid Fire"]
        self.assertTrue(WeaponTextGenerator.generate_weapon_attribute_text(weapon, 0).endswith("Reliable, Rapid Fire"))
        weapon.traits = []
        self.assertTrue(WeaponTextGenerator.generate_weapon_attribute_text(weapon, 0).endswith(" / "))

    def test_invalid_range_and_damage(self):
        # Verify missing/incompatible ranges and nonnumeric damage fail rather than generate misleading text.
        weapon = Weapon(**weapon_data())
        for distance in (None, MeleeRange()):
            weapon.range = distance
            with self.subTest(distance=distance), self.assertRaises(AttributeError):
                WeaponTextGenerator.get_range_text(weapon, 3)
        weapon.range = ShootingRange()
        weapon.damage = "invalid"
        with self.assertRaises(TypeError):
            WeaponTextGenerator.generate_weapon_attribute_text(weapon, 3)


class AbilityAndWeaponViewTests(QtTestCase):
    def test_ability_detail_and_remove_signal(self):
        # Verify ability title/body rendering, edit controls, and the remove signal's view payload.
        view = self.own(AbilityDetailView(Ability("Action", "Strike", "Attack"), 500))
        self.assertEqual(view.title_label.text(), "<b>ACTION: Strike</b>")
        self.assertEqual(view.attributes_label.text(), "Attack")
        removed = Mock()
        view.remove_ability_clicked.connect(removed)
        for enabled in (True, False):
            view.setEditMode(enabled)
            self.assertEqual(view.edit_btn.isHidden(), not enabled)
            self.assertEqual(view.remove_btn.isHidden(), not enabled)
        view.setEditMode(True)
        view.remove_btn.click()
        removed.assert_called_once_with(view)

    def test_weapon_detail_and_remove_signal(self):
        # Verify weapon title/stats rendering, edit controls, and the remove signal's view payload.
        weapon = Weapon(**weapon_data())
        view = self.own(WeaponDetailView(weapon, 3, 500))
        self.assertEqual(view.title_label.text(), "<b>Lasrifle:</b>")
        self.assertEqual(view.attributes_label.text(), "7 + 1 ED / AP -1 / Range 12-24-36 / Reliable")
        removed = Mock()
        view.remove_weapon_clicked.connect(removed)
        view.setEditMode(True)
        self.assertFalse(view.remove_weapon_btn.isHidden())
        view.remove_weapon_btn.click()
        removed.assert_called_once_with(view)
        view.setEditMode(False)
        self.assertTrue(view.remove_weapon_btn.isHidden())

    def test_ability_collection_removal(self):
        # Verify removing an ability updates both the child view list and the NPC ability list.
        model = make_npc()
        ability = Ability("Action", "Strike", "Attack")
        model.abilities = [ability]
        view = self.own(NpcAbilityView(model, 500))
        self.assertEqual(view.edit_btn.text(), "Add Ability")
        self.assertEqual(len(view.abilities), 1)
        child = view.abilities[0]
        view.setEditMode(True)
        self.assertFalse(child.remove_btn.isHidden())
        child.remove_btn.click()
        self.assertEqual(view.abilities, [])
        self.assertEqual(model.abilities, [])
        self.assertEqual(view.main_layout.indexOf(child), -1)

    def test_weapon_collection_removal(self):
        # Verify removing a weapon updates both the child view list and the NPC weapon list.
        model = make_npc()
        model.weapons = [Weapon(**weapon_data())]
        view = self.own(NpcWeaponView(model, 500))
        self.assertEqual(view.edit_btn.text(), "Add Weapons")
        child = view.weapons[0]
        view.setEditMode(True)
        self.assertFalse(child.remove_weapon_btn.isHidden())
        child.remove_weapon_btn.click()
        self.assertEqual(view.weapons, [])
        self.assertEqual(model.weapons, [])
        self.assertEqual(view.main_layout.indexOf(child), -1)

    def test_empty_collections_and_add_placeholders(self):
        # Verify empty collections render without children and current add placeholders leave models unchanged.
        model = make_npc()
        abilities = self.own(NpcAbilityView(model, 500))
        weapons = self.own(NpcWeaponView(model, 500))
        abilities.add_ability_clicked()
        weapons.add_weapon_clicked()
        self.assertEqual(abilities.abilities, [])
        self.assertEqual(weapons.weapons, [])
        self.assertEqual(model.abilities, [])
        self.assertEqual(model.weapons, [])


class DetailViewTests(QtTestCase):
    def test_initial_state_and_subviews(self):
        # Verify detail views start read-only, display the NPC name, and create all five subviews.
        model = make_npc()
        view = self.own(NpcDetailView(model, 600))
        self.assertIs(view.model, model)
        self.assertFalse(view.is_editing)
        self.assertTrue(view.name_field.isReadOnly())
        self.assertEqual(view.name_field.text(), model.name)
        self.assertEqual(len(view.view_parts), 5)
        self.assertTrue(view.cancel_btn.isHidden())

    def test_edit_save_and_cancel_state(self):
        # Verify edit/save/cancel clicks toggle the name field, controls, and child editing state.
        view = self.own(NpcDetailView(make_npc(), 600))
        view.edit_and_save_btn.click()
        self.assertTrue(view.is_editing)
        self.assertEqual(view.edit_and_save_btn.text(), "Save")
        self.assertFalse(view.name_field.isReadOnly())
        self.assertFalse(view.cancel_btn.isHidden())
        self.assertTrue(view.view_parts[0].attributes[0].isEnabled())
        view.edit_and_save_btn.click()
        self.assertFalse(view.is_editing)
        self.assertEqual(view.edit_and_save_btn.text(), "Edit")
        self.assertFalse(view.view_parts[0].attributes[0].isEnabled())
        view.edit_and_save_btn.click()
        view.cancel_btn.click()
        self.assertFalse(view.is_editing)
        self.assertTrue(view.cancel_btn.isHidden())

    def test_name_signal_and_model_update(self):
        # Verify editing the name updates the shared model and emits the new name once.
        model = make_npc()
        view = self.own(NpcDetailView(model, 600))
        changed = Mock()
        view.nameChanged.connect(changed)
        view.name_field.textEdited.emit("Veteran")
        self.assertEqual(model.name, "Veteran")
        changed.assert_called_once_with("Veteran")

    def test_custom_picture(self):
        # Verify a supplied NPC pixmap is rendered with preserved aspect ratio inside the picture bounds.
        model = make_npc()
        model.picture = QPixmap(300, 100)
        model.picture.fill(QColor("red"))
        view = self.own(NpcDetailView(model, 600))
        pictures = [label.pixmap() for label in view.findChildren(QLabel)
                    if label.size() == view.picture_size]
        self.assertEqual(len(pictures), 1)
        self.assertEqual((pictures[0].width(), pictures[0].height()), (150, 50))

    @unittest.expectedFailure
    def test_cancel_restores_model(self):
        # Verify cancel restores the original NPC name; currently no model rollback is implemented.
        model = make_npc()
        original = model.name
        view = self.own(NpcDetailView(model, 600))
        view.edit_and_save_btn.click()
        view.name_changed("Changed")
        view.cancel_btn.click()
        self.assertEqual(model.name, original)


class NpcTabTests(QtTestCase):
    def setUp(self):
        super().setUp()
        factory = patch("Windows.NPCTab.NpcTab.NpcDB", autospec=True)
        self.database_factory = factory.start()
        self.addCleanup(factory.stop)
        examples = patch("Windows.NPCTab.NpcTab.ExampleNPCs",
                         SimpleNamespace(KER=make_npc(), Skarn=make_npc()))
        examples.start()
        self.addCleanup(examples.stop)

    def test_initial_state_with_mocked_database(self):
        # Verify the tab constructs only a mocked database and initially displays its selection placeholder.
        tab = self.own(NpcTab())
        self.database_factory.assert_called_once_with()
        self.assertEqual(self.database_factory.return_value.mock_calls, [])
        self.assertIsNone(tab.npc_detail_view)
        self.assertEqual(tab.dummy_view.text(), "Nothing selected")
        self.assertEqual(tab.tab_list_view.list_widget.count(), 3)

    def test_selection_creates_and_replaces_detail(self):
        # Verify selecting list entries creates then replaces the detail view and disconnects the old name signal.
        tab = self.own(NpcTab())
        tab.tab_list_view.list_widget.setCurrentRow(1)
        first = tab.npc_detail_view
        self.assertIs(first.model, tab.tab_list_view.list_widget.item(1).model)
        self.assertTrue(tab.dummy_view.isHidden())
        tab.tab_list_view.list_widget.setCurrentRow(2)
        second = tab.npc_detail_view
        self.assertIsNot(first, second)
        self.assertIsNone(first.parent())
        self.own(first)
        with patch.object(tab.tab_list_view.list_widget.currentItem(), "updateTextWithModelName") as refresh:
            first.nameChanged.emit("Old")
            refresh.assert_not_called()
            second.name_changed("New")
            refresh.assert_called_once()
        self.assertEqual(self.database_factory.return_value.mock_calls, [])


if __name__ == "__main__":
    unittest.main()
