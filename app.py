import sys

from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtWidgets import QApplication

from lib.components.main_window import MainWindow
from lib.stores.theme_store import theme_store


def main():
    app = QApplication(sys.argv)
    # Optionally, set environment variables for scaling
    theme_store.app = app

    app.setApplicationName('App')
    app.setApplicationVersion('1.0.0')

    # Fonts laden
    font_id = QFontDatabase.addApplicationFont("assets/fonts/Roboto-Regular.ttf")  # default
    QFontDatabase.addApplicationFont("assets/fonts/Roboto-Bold.ttf")
    QFontDatabase.addApplicationFont("assets/fonts/Raleway-SemiBold-Light.ttf")
    QFontDatabase.addApplicationFont("assets/fonts/Raleway-SemiBold-Regular.ttf")
    if font_id != -1:  # Check if the font was loaded successfully
        family = QFontDatabase.applicationFontFamilies(font_id)[0]  # Get the font family name
        custom_font = QFont(family)
        app.setFont(custom_font)  # Apply font globally
    else:
        print("Failed to load the font!")

    # Create and show the main window
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    # Set DPI Awareness

    # Initialize ThemeManager and detect system theme
    if theme_store.dark_mode:
        sys.argv += ['-platform', 'windows:darkmode=2']
    else:
        sys.argv += ['-platform', 'windows:darkmode=0']

    main()
