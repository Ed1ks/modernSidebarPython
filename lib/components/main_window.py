from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from lib.components.sidebar import Sidebar
from lib.stores.theme_store import theme_store

from lib.views.home_view import HomeView
from lib.views.example1_view import Example1View
from lib.views.example2_view import Example2View
from lib.views.example3_view import Example3View


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Sidebar")
        self.setGeometry(2800, 100, 1200, 720)

        theme_store.window = self
        self.current_view = None

        # Sidebar and Content Area
        self.sidebar = Sidebar(self)

        # Create a content area
        self.content_area = QWidget()
        self.content_area.setObjectName("ContentArea")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Store views in a dictionary for reuse
        self.views = {
            "home": HomeView(self.content_area),
            "example1": Example1View(self.content_area),
            "example2": Example2View(self.content_area),
            "example3": Example3View(self.content_area),
        }

        # Add all views to the layout but make them initially invisible
        for view in self.views.values():
            self.content_layout.addWidget(view)
            view.setVisible(False)

        # Layout for MainWindow
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.content_area, stretch=1)

        self.setCentralWidget(central_widget)

        # Initialize ThemeManager
        if theme_store.dark_mode:
            theme_store.apply_dark_theme(self)
        else:
            theme_store.apply_light_theme(self)

        # Set default view
        self.set_view("home")

    def set_view(self, view_key):
        """Set the main view in the content area by view key."""
        if view_key not in self.views:
            print(f"Invalid view key: {view_key}")
            return  # Invalid view key, do nothing

        # Avoid reloading the current view
        if self.current_view == view_key:
            return

        # Hide the current view
        if self.current_view:
            self.views[self.current_view].setVisible(False)

        # Show the selected view
        self.views[view_key].setVisible(True)
        self.current_view = view_key
        self.sidebar.highlight_nav_button(view_key)
