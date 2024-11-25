import json

from PyQt5.QtWidgets import (
    QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QPushButton, QComboBox, QCheckBox, QCalendarWidget, QTimeEdit,
    QFormLayout, QLineEdit, QLabel, QTextEdit, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QDate, QTime, Qt, QTimer


class VersionHistoryWindow(QWidget):
    def __init__(self, parent=None, conn=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("Task Version History")
        self.setGeometry(200, 200, 600, 400)

        # Enable system decorations (close button, minimize, etc.)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowTitleHint)

        # Apply a custom border style (can be adjusted as per your design needs)
        #self.setStyleSheet("border: 2px solid #000000; border-radius: 10px;")

        # Layout setup
        self.layout = QVBoxLayout()

        # Date Selector
        self.date_selector = QCalendarWidget()
        self.date_selector.setGridVisible(True)
        self.date_selector.clicked.connect(self.load_tasks_for_date)
        self.layout.addWidget(QLabel("Select Date:"))
        self.layout.addWidget(self.date_selector)

        # Task Table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(3)
        self.task_table.setHorizontalHeaderLabels(["Task Name", "Version Date", "Details"])
        self.layout.addWidget(self.task_table)

        self.setLayout(self.layout)

    def load_tasks_for_date(self, selected_date):
        # Query tasks for the selected date
        selected_date_str = selected_date.toString("yyyy-MM-dd")
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT task_name, version_date, version_data
            FROM task_versions
            WHERE DATE(version_date) = ?
            ORDER BY version_date ASC
        """, (selected_date_str,))
        tasks = cursor.fetchall()

        # Populate the table with tasks
        self.task_table.setRowCount(0)  # Clear existing rows
        for row_index, (task_name, version_date, version_data) in enumerate(tasks):
            self.task_table.insertRow(row_index)
            self.task_table.setItem(row_index, 0, QTableWidgetItem(task_name))
            self.task_table.setItem(row_index, 1, QTableWidgetItem(version_date))

            # Add a "View" button to display task details
            view_button = QPushButton("View")
            view_button.clicked.connect(lambda _, data=version_data: self.show_task_details(data))
            self.task_table.setCellWidget(row_index, 2, view_button)

    def show_task_details(self, version_data):
        # Display task details in a message box
        task_details = json.loads(version_data)
        details_text = "\n".join([f"{key}: {value}" for key, value in task_details.items()])
        QMessageBox.information(self, "Task Details", details_text)