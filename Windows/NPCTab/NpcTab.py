from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Slot
from DatabaseManagement.NpcDB import NpcDB
from TestData import ExampleNPCs
from Windows.NPCTab.NpcDetailView import NpcDetailView
from Windows.TabListView import TabListView, TabTreeModel


class NpcTab(QWidget):
    """Tab to interact with Npcs"""

    tab_title = "Npcs"
    sub_widget_width = 600

    def __init__(self):
        super().__init__()

        database = NpcDB()

        # TODO Replace with real data
        example_npcs = [ExampleNPCs.KER, ExampleNPCs.Skarn]
        example_npcs[0].picture = QPixmap("TestData/Cyberchar.jpeg")

        npc_model = TabTreeModel(example_npcs)

        # Layout
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.tab_list_view = TabListView(self.tab_title, npc_model, self)
        self.tab_list_view.selectedItemChanged.connect(self.selection_changed)
        self.main_layout.addWidget(self.tab_list_view)

        self.npc_detail_view = None

        self.dummy_view = QLabel("Nothing selected")
        self.dummy_view.setFixedWidth(self.sub_widget_width)
        self.main_layout.addWidget(self.dummy_view)

    @Slot(object)
    def selection_changed(self, item: object):

        if self.npc_detail_view is None:
            self.npc_detail_view = NpcDetailView(item, self.sub_widget_width)
            self.main_layout.replaceWidget(self.dummy_view, self.npc_detail_view)
            self.dummy_view.hide()
            self.npc_detail_view.nameChanged.connect(self.tab_list_view.tree_item_name_changed)
        else:
            self.npc_detail_view.nameChanged.disconnect(self.tab_list_view.tree_item_name_changed)
            new_view = NpcDetailView(item, self.sub_widget_width)
            self.main_layout.replaceWidget(self.npc_detail_view, new_view)
            self.npc_detail_view.setParent(None)
            self.npc_detail_view = new_view
            self.npc_detail_view.nameChanged.connect(self.tab_list_view.tree_item_name_changed)




