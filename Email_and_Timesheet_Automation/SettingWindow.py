from PyQt5.QtWidgets import (
    QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QPushButton, QComboBox, QCheckBox, QCalendarWidget, QTimeEdit,
    QFormLayout, QLineEdit, QLabel, QTextEdit, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QDate, QTime, Qt, QTimer, pyqtSignal
import json
import os


class SettingsWindow(QWidget):
    settings_updated = pyqtSignal()  # Signal to notify when settings are updated

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(150, 150, 500, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowTitleHint)

        self.parent = parent
        self.layout = QVBoxLayout()

        # Functional Area Config
        self.functional_area_input = QTextEdit()
        self.functional_area_input.setText(",".join(self.parent.settings.get("functional_areas", [])))
        self.layout.addWidget(QLabel("Functional Areas"))
        self.layout.addWidget(self.functional_area_input)

        # Assignment Config
        self.assignment_input = QTextEdit()
        self.assignment_input.setText(",".join(self.parent.settings.get("assignments", [])))
        self.layout.addWidget(QLabel("Assignments"))
        self.layout.addWidget(self.assignment_input)

        # Task Type Config
        self.task_type_input = QTextEdit()
        self.task_type_input.setText(",".join(self.parent.settings.get("task_types", [])))
        self.layout.addWidget(QLabel("Task Types"))
        self.layout.addWidget(self.task_type_input)


        self.email_to_user = QTextEdit()
        self.email_to_user.setText(",".join(self.parent.settings.get("to_user", [])))
        self.layout.addWidget(QLabel("Send To"))
        self.layout.addWidget(self.email_to_user)

        self.cc_email_to_user = QTextEdit()
        self.cc_email_to_user.setText(",".join(self.parent.settings.get("cc_user", [])))
        self.layout.addWidget(QLabel("CC"))
        self.layout.addWidget(self.cc_email_to_user)


        # Webhook URL
        self.webhook_url_input = QLineEdit()
        self.webhook_url_input.setText(self.parent.settings.get("webhook_url", ""))
        self.layout.addWidget(QLabel("Webhook URL"))
        self.layout.addWidget(self.webhook_url_input)

        # Role
        self.role_input = QLineEdit()
        self.role_input.setText(self.parent.settings.get("role", ""))
        self.layout.addWidget(QLabel("Role"))
        self.layout.addWidget(self.role_input)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setText(self.parent.settings.get("name", ""))
        self.layout.addWidget(QLabel("Name"))
        self.layout.addWidget(self.name_input)

        # Mobile No
        self.mobile_input = QLineEdit()
        self.mobile_input.setText(self.parent.settings.get("mobile_no", ""))
        self.layout.addWidget(QLabel("Mobile No"))
        self.layout.addWidget(self.mobile_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setText(self.parent.settings.get("email", ""))
        self.layout.addWidget(QLabel("Email"))
        self.layout.addWidget(self.email_input)

        # Monthly Timesheet
        self.timesheet_input = QLineEdit()
        self.timesheet_input.setText(self.parent.settings.get("timesheet_link", ""))
        self.layout.addWidget(QLabel("Monthly Timesheet Link"))
        self.layout.addWidget(self.timesheet_input)

        # Email Scheduling Time
        self.schedule_time_input = QTimeEdit()
        self.schedule_time_input.setDisplayFormat("HH:mm")
        self.schedule_time_input.setTime(QTime.fromString(self.parent.settings.get("schedule_time", "09:00"), "HH:mm"))
        self.layout.addWidget(QLabel("Email Schedule Time"))
        self.layout.addWidget(self.schedule_time_input)

        # Save Button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_settings(self):
        functional_areas = self.functional_area_input.toPlainText().split(',')
        assignments = self.assignment_input.toPlainText().split(',')
        task_types = self.task_type_input.toPlainText().split(',')
        schedule_time = self.schedule_time_input.time().toString("HH:mm")
        webhook_url = self.webhook_url_input.text()
        to_user = self.email_to_user.toPlainText().split(',')
        cc_user = self.cc_email_to_user.toPlainText().split(',')

        # Additional fields
        role = self.role_input.text()
        name = self.name_input.text()
        mobile_no = self.mobile_input.text()
        email = self.email_input.text()
        timesheet = self.timesheet_input.text()

        # Save to a configuration file
        config = {
            "functional_areas": functional_areas,
            "assignments": assignments,
            "task_types": task_types,
            "schedule_time": schedule_time,
            "webhook_url": webhook_url,
            "to_user": to_user,
            "cc_user": cc_user,
            "role": role,
            "name": name,
            "mobile_no": mobile_no,
            "email": email,
            "timesheet_link": timesheet
        }

        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "../settings.json")



        try:
            with open(config_path, "w+") as config_file:
                json.dump(config, config_file, indent=4)
            QMessageBox.information(self, "Success", "Settings have been saved.")
            print(json.dumps(config, indent=4))  # Ensure config is populated correctly

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

        # Emit the signal to notify the main window
        self.settings_updated.emit()
        self.close()
