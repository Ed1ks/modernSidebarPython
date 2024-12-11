import platform

from PySide6.QtCore import QFile, QIODevice, QTextStream
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

from lib.stores.icon_store import icon_store


def detect_system_theme() -> bool:
    """Detect the system's theme preference."""
    if platform.system() == "Windows":
        # Check Windows registry for theme settings
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0  # 0 = Dark Mode, 1 = Light Mode
        except (Exception,):
            return False  # Default to light mode on error

    elif platform.system() == "Darwin":
        # macOS dark mode detection
        try:
            import subprocess
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return "Dark" in result.stdout
        except (Exception,):
            return False  # Default to light mode on error

    else:
        # Assume light mode for Linux (extend with specific DE checks if needed)
        return False


class ThemeStore:

    def __init__(self):
        self.app = None
        self.window = None
        self.dark_mode = detect_system_theme()

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        if theme_store.dark_mode:
            self.apply_light_theme(theme_store.window)
        else:
            self.apply_dark_theme(theme_store.window)

        icon_store.update_icons(theme_store.dark_mode)

    def apply_light_theme(self, window):
        """Apply the light theme."""
        theme_store.dark_mode = False
        self.app.setStyleSheet(self.get_light_qss())

        # Create shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(13)
        shadow.setColor(QColor(0, 0, 0, 150))  # Semi-transparent black
        shadow.setOffset(5, 0)  # Shadow to the right
        self.window.content_area.setGraphicsEffect(shadow)

    def apply_dark_theme(self, window):
        """Apply the dark theme."""
        theme_store.dark_mode = True
        self.app.setStyleSheet(self.get_dark_qss())

        # Create shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(14)
        shadow.setColor(QColor(255, 255, 255, 150))  # Semi-transparent black
        shadow.setOffset(5, 0)  # Shadow to the right
        self.window.content_area.setGraphicsEffect(shadow)

    @staticmethod
    def get_light_qss():
        """QSS for light mode."""

        file = QFile("assets/styles/style--light.css")
        file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text)
        stream = QTextStream(file)
        return stream.readAll()

    @staticmethod
    def get_dark_qss():
        """QSS for dark mode."""

        file = QFile("assets/styles/style--dark.css")
        file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text)
        stream = QTextStream(file)
        return stream.readAll()


# Singleton-Instanz
theme_store = ThemeStore()
