from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QFrame, QLabel,
    QPushButton, QComboBox, QHBoxLayout, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon


class HomeView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_edit_mode = False  # Track edit mode state
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create a card-like frame
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)

        # Add title and edit button above the table
        title_layout = QHBoxLayout()
        title = QLabel("User Information")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title)

        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.toggle_edit_mode)
        title_layout.addWidget(self.edit_button, alignment=Qt.AlignRight)

        card_layout.addLayout(title_layout)

        # Add table to the card
        self.table = QTableWidget(3, 3)  # Three columns: Name, Age, Actions
        self.table.setHorizontalHeaderLabels(["Name", "Age", "Actions"])
        self.table.setItem(0, 0, QTableWidgetItem("Alice"))
        self.table.setItem(0, 1, QTableWidgetItem("25"))
        self.add_delete_button(0)

        self.table.setItem(1, 0, QTableWidgetItem("Bob"))
        self.table.setItem(1, 1, QTableWidgetItem("30"))
        self.add_delete_button(1)

        self.table.setItem(2, 0, QTableWidgetItem("Charlie"))
        self.table.setItem(2, 1, QTableWidgetItem("35"))
        self.add_delete_button(2)

        # Hide the row numbers
        self.table.verticalHeader().setVisible(False)

        # Adjust column stretching and styling
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable editing by default
        self.table.cellDoubleClicked.connect(self.handle_double_click)

        card_layout.addWidget(self.table)

        # Add "Neu" button below the table
        self.add_row_button = QPushButton("Neu")
        self.add_row_button.setStyleSheet("padding: 5px 10px; font-size: 12px;")
        self.add_row_button.clicked.connect(self.add_row)
        card_layout.addWidget(self.add_row_button, alignment=Qt.AlignCenter)

        # Add card to the main layout
        layout.addWidget(card)
        layout.addStretch()

    def add_row(self):
        """Add a new row to the table with default values."""
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        self.table.setItem(row_count, 0, QTableWidgetItem("New User"))
        self.table.setItem(row_count, 1, QTableWidgetItem("0"))  # Default Age
        self.add_delete_button(row_count)

    def add_delete_button(self, row):
        """Add a delete button in the last column of a row."""
        delete_button = QPushButton()
        icon_path = (
            "assets/icons/trash_gray.png" if not self.is_edit_mode else "assets/icons/trash_red.png"
        )
        delete_button.setIcon(QIcon(icon_path))  # Use appropriate icon
        delete_button.setStyleSheet("border: none; background: transparent; padding: 5px;")
        delete_button.clicked.connect(lambda: self.confirm_delete(row))
        delete_button.setProperty("row", row)  # Store the row number
        self.table.setCellWidget(row, 2, delete_button)

    def confirm_delete(self, row):
        """Show a confirmation dialog and delete the row if confirmed."""
        if not self.is_edit_mode:
            return  # Only allow deletion in edit mode

        reply = QMessageBox.question(
            self,
            "Delete Row",
            "Are you sure you want to delete this row?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.table.removeRow(row)

    def toggle_edit_mode(self):
        """Enable or disable editing for the table."""
        self.is_edit_mode = not self.is_edit_mode
        # Update delete button icons based on edit mode
        for row in range(self.table.rowCount()):
            self.add_delete_button(row)

        if self.is_edit_mode:
            self.table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
            self.edit_button.setText("Stop Editing")
        else:
            self.table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.edit_button.setText("Edit")

    def handle_double_click(self, row, column):
        """Enable dropdown in the second column on double-click, only in edit mode."""
        if not self.is_edit_mode or column != 1:
            return  # Only allow in edit mode and for the second column

        combo = QComboBox()
        combo.addItems(["18", "25", "30", "35", "40", "50"])
        combo.setCurrentText(self.table.item(row, column).text())
        combo.currentIndexChanged.connect(lambda: self.update_cell_with_dropdown(row, column, combo))
        self.table.setCellWidget(row, column, combo)

    def update_cell_with_dropdown(self, row, column, combo):
        """Update the table cell with the selected value from the dropdown."""
        selected_value = combo.currentText()
        self.table.setItem(row, column, QTableWidgetItem(selected_value))
        self.table.setCellWidget(row, column, None)  # Remove the combo box
