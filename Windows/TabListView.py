from PySide6.QtGui import QColor, Qt, QIcon, QPixmap
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QTreeView, QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QListWidget, \
    QListWidgetItem, QLineEdit, QHBoxLayout, QStyle

from Data import IsGroupable

class TabTreeModel():

    def __init__(self, data: list[IsGroupable.HasGroup]):
        super().__init__()

        self.data = data
        self.grouped_data = {}

        for item in data:
            if not self.grouped_data.__contains__(item.group):
                self.grouped_data.update({item.group: [item]})
            else:
                self.grouped_data[item.group].append(item)
class GroupItem(QListWidgetItem):
    def __init__(self, group_name):
        super().__init__(group_name)
        self.setBackground(QColor("lightgrey"))
        self.setFlags(self.flags() & ~Qt.ItemIsSelectable)

        self.childItems = []

    def append(self, item):
        self.childItems.append(item)

    def all_children_hidden(self):
        for child in self.childItems:
            if not child.isHidden():
                return True
        return False

class TreeItem(QListWidgetItem):

    padding = "  "

    def __init__(self, model, ):
        super().__init__("  " + model.name)
        self.model = model

    def updateTextWithModelName(self):
        self.setText("  " + self.model.name)

class TabListView(QWidget):
    """General class to have a tree view in a tab GUI"""

    selectedItemChanged = Signal(object)
    """Is triggered when another item is selected"""

    def __init__(self, title, model: TabTreeModel, parent=None):
        super(TabListView, self).__init__(parent)

        # Layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(QLabel(title))

        search_bar = QLineEdit(placeholderText="Search")
        pixmap = QPixmap("Icons/search.png")
        icon_label = QLabel(pixmap= pixmap.scaledToHeight(15))
        search_bar.textEdited.connect(self.update_display)

        sublayout = QHBoxLayout()
        sublayout.addWidget(search_bar)
        sublayout.addWidget(icon_label)
        main_layout.addLayout(sublayout)

        self.list_widget = QListWidget()
        current_id = 0

        # Create content to display
        self.group_items = []
        for group in model.grouped_data:
            group_item = GroupItem(group)
            self.list_widget.addItem(group_item)
            self.group_items.append(group_item)
            # Add all children
            for item in model.grouped_data[group]:
                tree_item = TreeItem(item)
                self.list_widget.addItem(tree_item)
                group_item.append(tree_item)

        main_layout.addWidget(self.list_widget)
        self.list_widget.itemSelectionChanged.connect(self.selection_changed)

    def update_display(self, text):
        """Update the display of the tab list"""
        search = text.strip().casefold()
        for group in self.group_items:
            txt = group.text()
            cased = txt.casefold()
            if search in group.text().casefold() :
                group.setHidden(False)
                for item in group.childItems:
                    item.setHidden(False)
            else:
                should_hide = True
                for item in group.childItems:
                    if search in item.text().casefold() :
                        item.setHidden(False)
                        should_hide = False
                    else:
                        item.setHidden(True)
                group.setHidden(should_hide)

    @Slot(object)
    def selection_changed(self):
        #TODO Check if changed and if popup
        if isinstance(self.list_widget.currentItem(), TreeItem):
            self.selectedItemChanged.emit(self.list_widget.currentItem().model)

    @Slot(str)
    def tree_item_name_changed(self, text):
        self.list_widget.currentItem().updateTextWithModelName()