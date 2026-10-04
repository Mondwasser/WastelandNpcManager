from PySide6.QtWidgets import QPushButton, QStyle

class DeleteButton(QPushButton):
    def __init__(self, size: int = 16):
        super().__init__()

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
        self.setIcon(icon)
        self.setFixedSize(size, size)
        self.setStyleSheet(f""" QPushButton {{border-radius: {size // 2}px;}}""")