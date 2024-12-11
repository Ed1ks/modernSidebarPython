from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)


class Example3View(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        label = QLabel("Example Page 3")
        label.setStyleSheet("font-size: 16px;")
        layout.addWidget(label)

