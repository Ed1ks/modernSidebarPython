from PySide6.QtCore import QPropertyAnimation, QSize, Qt, QRect, QEvent, QPoint, Property
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFrame, QLabel

from lib.components.nav_context_menu import NavContextMenu
from lib.stores.icon_store import icon_store, IconUpdateCallback
from lib.stores.theme_store import theme_store


class Sidebar(QWidget):
    @property
    def sidebar_width(self):
        return self._sidebar_width

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.expanded = True  # Sidebar startet ausgeklappt

        # Sidebar-Eigenschaften
        self._width = 220  # Initiale Breite
        self.setFixedWidth(self._width)
        self.nav_button_size = QSize(40, 40)  # Einheitliche Button-Größe
        self.setObjectName("Sidebar")

        # Hauptlayout der Sidebar
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        # Top-Bar mit Snack- und Theme-Toggle-Buttons
        self.top_bar = QFrame()
        self.top_bar_layout = QVBoxLayout(self.top_bar)  # Standard vertikale Anordnung
        self.top_bar_layout.setContentsMargins(5, 5, 5, 5)
        self.top_bar_layout.setSpacing(5)

        # Sidebar-Toggle-Button
        self.snack_button = QPushButton()
        self.snack_button.setIcon(icon_store.load_iconify_icon(icon_name="menu", dark_mode=theme_store.dark_mode, widget=self.snack_button))
        self.snack_button.setFixedSize(self.nav_button_size)
        self.snack_button.setObjectName("IconButton")
        self.snack_button.clicked.connect(self.toggle_sidebar)
        self.top_bar_layout.addWidget(self.snack_button)

        # Theme-Toggle-Button
        self.theme_button = QPushButton()
        self.theme_button.setIcon(icon_store.load_iconify_icon(icon_name="moon", dark_mode=theme_store.dark_mode, widget=self.theme_button, icon_name_dark="sun"))
        self.theme_button.setFixedSize(self.nav_button_size)
        self.theme_button.setObjectName("IconButton")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.top_bar_layout.addWidget(self.theme_button)

        self.layout.addWidget(self.top_bar)

        # Menüeinträge
        self.menu = [
            {"title": "Home", "view_key": "home", "icon": "workschedule_generator", "submenu": []},
            {"title": "Settings", "view_key": None, "icon": "settings", "submenu": [
                {"title": "Example 2", "view_key": "example1", "icon": "template"},
                {"title": "Example 3", "view_key": "example2", "icon": "workschedule_generator"},
            ]},
            {"title": "Example 4", "view_key": "example3", "icon": "template", "submenu": []},
        ]

        self.nav_buttons = {}
        self.menu_arrows: [QLabel] = []
        self.generate_menu()

        # Stretch für flexible Layout-Anpassung
        self.layout.addStretch()

        # Callback um die Icons zu färben
        icon_store.icon_update_callbacks.append(IconUpdateCallback(lambda: self.highlight_nav_button(self.main_window.current_view)))

        # Standard-Button hervorheben
        self.update_menu_visibility()

    @Property(int)
    def sidebar_width(self):
        return self._width

    @sidebar_width.setter
    def sidebar_width(self, width):
        self._width = width
        self.setFixedWidth(width)

    def toggle_sidebar(self):
        """Sidebar ein- und ausklappen mit Animation."""
        self.expanded = not self.expanded
        start_width = self.sidebar_width
        end_width = 220 if self.expanded else 50

        # Animation für die Breite
        self.animation = QPropertyAnimation(self, b"sidebar_width")
        self.animation.setDuration(80)
        self.animation.setStartValue(start_width)
        self.animation.setEndValue(end_width)
        self.animation.start()

        # Widgets erst nach Abschluss der Animation aktualisieren
        self.animation.finished.connect(self.update_menu_visibility)

    def update_menu_visibility(self):
        """Aktualisiert die Sichtbarkeit und den Text von Buttons basierend auf dem Sidebar-Zustand."""
        # Passe die Top-Bar-Ausrichtung an
        self.top_bar_layout.setDirection(QVBoxLayout.TopToBottom if not self.expanded else QHBoxLayout.LeftToRight)

        for item in self.menu:
            button = self.nav_buttons.get(item["title"])
            if button:
                if self.expanded:
                    # Großer Sidebar-Zustand
                    button.setText(item["title"])
                    button.setIconSize(QSize(24, 24))
                    if item["submenu"]:
                        submenu_container = button.property("submenu_container")
                        if submenu_container:
                            submenu_container.setVisible(True)
                            button.setEnabled(False)  # Hauptmenü nicht anklickbar

                    # alle Pfeile verstecken
                    for label_arrow in self.menu_arrows:
                        label_arrow.setVisible(False)
                else:
                    # Eingeklappter Sidebar-Zustand
                    button.setText("")  # Entferne Text im eingeklappten Zustand
                    button.setIconSize(QSize(32, 32))
                    if item["submenu"]:
                        submenu_container = button.property("submenu_container")
                        if submenu_container:
                            submenu_container.setVisible(False)
                            button.setEnabled(True)  # Hauptmenü anklickbar
                    icon_store.update_icons(theme_store.dark_mode)  # fixt die Button-Größe

                    # alle Pfeile anzeigen
                    for label_arrow in self.menu_arrows:
                        label_arrow.setVisible(True)

        self.highlight_nav_button(self.main_window.current_view)

    def generate_menu(self):
        """Generiert das Menü basierend auf der Menüstruktur."""
        for item in self.menu:
            if not item["submenu"]:
                self.add_nav_button(item["title"], item["view_key"], item["icon"])
            else:
                self.add_submenu(item["title"], item["submenu"], item["icon"])

    def add_nav_button(self, label, view_key, icon_name):
        """Fügt einen Navigations-Button hinzu."""
        button = QPushButton()
        button.setObjectName("NavButton")
        button.setProperty("selected", False)
        button.setIcon(icon_store.load_iconify_icon(icon_name=icon_name, dark_mode=theme_store.dark_mode, widget=button))
        button.clicked.connect(lambda: self.set_view(view_key))
        self.nav_buttons[label] = button
        self.layout.addWidget(button)

    def add_submenu(self, title, submenu_items, icon_name):
        """Fügt Title und seine Submenüs hinzu."""
        # Hauptbutton für Submenü
        button = QPushButton()
        button.setObjectName("SubmenuTitle")
        button.setProperty("selected", False)
        button.setIcon(icon_store.load_iconify_icon(icon_name=icon_name, dark_mode=theme_store.dark_mode, widget=button))

        # Pfeil neben Hauptmenu
        overlay_icon = QLabel(button)
        # overlay_pixmap = QPixmap("assets/icons/arrow_menu_open.svg").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # overlay_icon.setPixmap(overlay_pixmap)
        overlay_icon.setPixmap(icon_store.load_iconify_icon(icon_name="arrow_menu_open", dark_mode=theme_store.dark_mode, widget=overlay_icon, size=24).pixmap(QSize(24, 24)))
        overlay_icon.setFixedSize(18, 18)
        overlay_icon.setAttribute(Qt.WA_TranslucentBackground)
        overlay_icon.setStyleSheet("padding: 0px; margin: 0px;")
        overlay_icon.setGeometry(32, 12, 16, 16)
        self.menu_arrows.append(overlay_icon)
        button.setProperty("overlay_icon_arrow", overlay_icon)

        self.nav_buttons[title] = button
        self.layout.addWidget(button)

        # Submenü-Container für große Sidebar
        submenu_container = QWidget()
        submenu_layout = QVBoxLayout(submenu_container)
        submenu_layout.setContentsMargins(10, 0, 0, 0)
        submenu_layout.setSpacing(5)

        for item in submenu_items:
            submenu_button = QPushButton(item["title"])
            submenu_button.setObjectName("SubNavButton")
            submenu_button.setProperty('view_key', item["view_key"])
            submenu_button.setIcon(icon_store.load_iconify_icon(icon_name=item["icon"], dark_mode=theme_store.dark_mode, widget=submenu_button))
            # submenu_button.setFixedHeight(self.nav_button_size.height())  # Gleiche Höhe wie Hauptmenüs
            submenu_button.clicked.connect(lambda _, key=item["view_key"]: self.set_view(key))
            submenu_layout.addWidget(submenu_button)

        self.layout.addWidget(submenu_container)
        button.setProperty("submenu_container", submenu_container)
        button.setProperty("submenu_items", submenu_items)
        button.setProperty("context_is_open", False)
        button.setProperty("mouse_pos", 0)
        button.setAttribute(Qt.WA_Hover, True)
        button.installEventFilter(self)

        # Kontextmenü für kleine Sidebar
        # button.clicked.connect(lambda: self.show_context_menu(button, submenu_items) if not self.expanded else None)

    def eventFilter(self, obj, event):
        if isinstance(obj, QPushButton) and obj.objectName() == "SubmenuTitle" and not self.expanded:
            submenu = obj.property("submenu")
            submenu_container = obj.property("submenu_container")
            submenu_items_prop = obj.property("submenu_items")
            context_is_open = obj.property("context_is_open")

            if submenu_container is not None:
                if event.type() == QEvent.HoverEnter and not context_is_open:
                    obj.setProperty("context_is_open", True)
                    submenu = self.show_context_menu(obj, submenu_items_prop)
                    submenu.setProperty("parent_button", obj)
                    obj.setProperty("submenu", submenu)
                elif event.type() == QEvent.HoverLeave and context_is_open and submenu:
                    global_pos = QCursor.pos()
                    button_geometry = QRect(obj.mapToGlobal(QPoint(0, 0)), obj.size())
                    if not submenu.geometry().contains(global_pos) and not button_geometry.contains(global_pos):
                        submenu.close()
                        obj.setProperty("context_is_open", False)
                        obj.setProperty("submenu", None)
                    # self.closeContextMenu()
        return super().eventFilter(obj, event)

    def show_context_menu(self, button, submenu_items):
        """Zeigt ein Kontextmenü für Submenüelemente."""
        if self.expanded:
            return  # Kein Kontextmenü, wenn Sidebar groß ist

        menu = NavContextMenu()
        menu.setObjectName("NavContextMenu")
        for item in submenu_items:
            submenu_button = menu.add_action(item["title"], icon=item["icon"], callback=lambda key=item["view_key"]: self.set_view(key))

            # Prüfen, ob Submenü aktiv ist
            is_active = item["view_key"] == self.main_window.current_view
            if is_active:
                submenu_button.setProperty("active", True)
                submenu_button.style().unpolish(submenu_button)
                submenu_button.style().polish(submenu_button)
                submenu_button.update()
                icon_store.update_icon_color_from_func(submenu_button, lambda: submenu_button.palette().color(submenu_button.foregroundRole()))

            # Verbindung für Klick
            #action.triggered.connect(lambda _, key=item["view_key"]: self.set_view(key))

        pos = button.mapToGlobal(button.rect().topRight())
        pos.setX(pos.x() + 1)
        menu.show_menu(pos)
        return menu

    def set_view(self, view_key):
        """Wechselt die Ansicht."""
        if view_key:
            self.main_window.set_view(view_key)

    def highlight_nav_button(self, active_key):
        """Hebt den aktiven Button hervor."""
        for item in self.menu:
            # Hauptmenüpunkt
            button = self.nav_buttons.get(item["title"])
            if not button:
                continue

            # Prüfen, ob der Hauptmenüpunkt aktiv ist oder eines seiner Submenüs aktiv ist
            is_active = item["view_key"] == active_key
            submenu_active = any(sub["view_key"] == active_key for sub in item.get("submenu", []))

            # Hauptmenüpunkt: Aktiv, wenn selbst aktiv oder (im kleinen Zustand) eines der Submenüs aktiv ist
            button_active = is_active or (submenu_active and not self.expanded)
            button.setProperty("selected", button_active)
            """refresh style"""
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

            overlay_icon_arrow = button.property("overlay_icon_arrow")
            if overlay_icon_arrow is not None:
                icon_store.update_icon_color_from_func(overlay_icon_arrow, lambda: button.palette().color(button.foregroundRole()))
                overlay_icon_arrow.style().unpolish(button)
                overlay_icon_arrow.style().polish(button)
                overlay_icon_arrow.update()

            """Color Icon"""
            icon_store.update_icon_color_from_func(button, lambda: button.palette().color(button.foregroundRole()))

            # Submenüs: Nur im großen Zustand aktiv
            if item.get("submenu"):
                if self.expanded:
                    submenu_container = button.property("submenu_container")
                    if submenu_container:
                        for i in range(submenu_container.layout().count()):
                            submenu_button = submenu_container.layout().itemAt(i).widget()
                            submenu_button_view_key = submenu_button.property("view_key")
                            if submenu_button:
                                # Prüfen, ob Submenü aktiv ist
                                submenu_active = submenu_button_view_key == active_key
                                submenu_button.setProperty("selected", submenu_active)
                                """refresh style"""
                                submenu_button.style().unpolish(submenu_button)
                                submenu_button.style().polish(submenu_button)
                                submenu_button.update()
                                # update icon
                                icon_store.update_icon_color_from_func(submenu_button, lambda: submenu_button.palette().color(submenu_button.foregroundRole()))

    @staticmethod
    def toggle_theme():
        """Schaltet das Theme der Anwendung um."""
        theme_store.toggle_theme()

