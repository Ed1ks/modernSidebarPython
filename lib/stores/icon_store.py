from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QLabel


class IconUpdateCallback:
    def __init__(self, function, *args, **kwargs):
        self.func = function
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.func(*self.args, **self.kwargs)


class IconStore:
    def __init__(self):
        self.icon_widgets = []  # Liste von Widgets und ihren Icon-Namen
        self.icon_update_callbacks: [IconUpdateCallback] = []  # Liste von Callback-Funktionen, z.B. um Farben zu aktualisieren

    def register(self, widget, icon_name):
        """Widget mit Icon im Store registrieren."""
        if (widget, icon_name) not in self.icon_widgets:
            self.icon_widgets.append((widget, icon_name))

    def update_icons(self, dark_mode):
        """Alle Icons im Store aktualisieren."""
        for widget, icon_name, size, icon_name_dark in self.icon_widgets:
            if isinstance(widget, QLabel):
                widget.setPixmap(self.load_iconify_icon(icon_name, dark_mode, size=size, icon_name_dark=icon_name_dark).pixmap(QSize(size, size)))
            else:
                widget.setIcon(self.load_iconify_icon(icon_name, dark_mode, size=size, icon_name_dark=icon_name_dark))

        """call callbacks after update_icons"""
        for callback in self.icon_update_callbacks:
            callback()

    def load_iconify_icon(self, icon_name, dark_mode, widget=None, size=32, icon_name_dark=None):
        """Lädt und färbt ein Icon basierend auf dem Modus."""
        if icon_name_dark is None:
            icon_name_dark = icon_name

        """if icon has dark mode version, load it"""
        load_icon_name = icon_name_dark if dark_mode and icon_name_dark is not None else icon_name
        icon_path = f"assets/icons/{load_icon_name}.svg"
        pixmap = QPixmap(icon_path)
        pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        """color it"""
        color = QColor("white" if dark_mode else "black")
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()

        # Wenn ein Widget übergeben wurde, füge es zur globalen Liste hinzu
        if widget and widget not in self.icon_widgets:
            self.icon_widgets.append((widget, icon_name, size, icon_name_dark))  # Speichere Widget und Icon-Name

        return QIcon(pixmap)

    @staticmethod
    def update_icon_color_from_func(widget, func):
        """Aktualisiert die Farbe des Icons eines Widgets basierend auf der angegebenen Farbe."""
        color = func()
        if isinstance(widget, QLabel):
            pixmap = widget.pixmap()
        else:
            pixmap = widget.icon().pixmap(widget.iconSize())
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()

        if isinstance(widget, QLabel):
            widget.setPixmap(pixmap)
        else:
            widget.setIcon(QIcon(pixmap))


# Singleton-Instanz
icon_store = IconStore()
