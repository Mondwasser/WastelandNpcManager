import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout

from Windows.NPCTab.NpcTab import NpcTab


# Main window of Wasteland NPC Manager
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Wasteland NPC Manager")

        # Main menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        #layout
        main_widget = NpcTab()
        layout = QVBoxLayout(main_widget)

        npc_bar = NpcTab()

        layout.addWidget(npc_bar)

        self.setCentralWidget(main_widget)

# Create and start application
app = QApplication(sys.argv)
app.setStyle('Fusion')
window = MainWindow()
window.show()
app.exec()