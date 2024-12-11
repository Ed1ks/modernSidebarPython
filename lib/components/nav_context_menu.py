from PySide6.QtCore import Qt, Signal, QRect, QPoint, QSize
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from lib.stores.icon_store import icon_store
from lib.stores.theme_store import theme_store


class NavContextMenu(QWidget):
    action_triggered = Signal(str)  # Signal for triggered action

    def __init__(self, object_name="CustomMenu"):
        super().__init__()
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setObjectName(object_name)  # Set a unique objectName for styling

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.installEventFilter(self)

    def add_action(self, text, icon, callback=None, active=False):
        """Add an action to the custom menu."""
        submenu_button = QPushButton(" " + text)

        # submenu_button = QLabel(text, self)
        # submenu_button.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        submenu_button.setIcon(icon_store.load_iconify_icon(icon_name=icon, dark_mode=theme_store.dark_mode, widget=submenu_button))

        submenu_button.setIconSize(QSize(32, 18))
        submenu_button.setContentsMargins(10, 10, 10, 10)
        submenu_button.setProperty('active', active)

        # Connect the mouse press event to trigger the callback
        submenu_button.mousePressEvent = lambda event: self._on_action_triggered(submenu_button, callback)

        self.layout.addWidget(submenu_button)
        return submenu_button

    def _on_action_triggered(self, label, callback):
        """Emit signal and trigger callback."""

        self.action_triggered.emit(label.text())
        self.set_button_active(label)

        if callback:  # If a callback is provided, invoke it
            callback()

    def set_button_active(self, active_button):
        active_button.setProperty("active", True)
        for i in range(self.layout.count()):
            button = self.layout.itemAt(i).widget()
            if button != active_button:
                button.setProperty("active", False)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()
            icon_store.update_icon_color_from_func(button, lambda: button.palette().color(button.foregroundRole()))

    def show_menu(self, pos):
        """Display the menu at the given position."""
        self.move(pos)
        self.adjustSize()
        self.show()

    def eventFilter(self, obj, event):
        parent_button = self.property("parent_button")
        if parent_button is None:
            return super().eventFilter(obj, event)

        global_pos = QCursor.pos()
        button_geometry = QRect(parent_button.mapToGlobal(QPoint(0, 0)), parent_button.size())
        if not self.geometry().contains(global_pos) and not button_geometry.contains(global_pos):
            parent_button.setProperty("context_is_open", False)
            parent_button.setProperty("submenu", None)
            self.close()  # Close the menu when the mouse leaves

        return super().eventFilter(obj, event)
