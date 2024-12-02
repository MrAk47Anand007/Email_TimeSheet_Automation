import json
import os

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QMessageBox, QLabel


class MomSettingsWindow(QDialog):
    """A simple settings window for managing email groups and webhook URL."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MOM Settings")
        self.setGeometry(200, 200, 600, 500)


        self.layout = QVBoxLayout()

        # Email Group Editor
        self.email_groups_editor = QTextEdit()
        self.email_groups_editor.setPlaceholderText(
            "Enter email groups with emails (e.g., Group1: email1@example.com; email2@example.com)"
        )
        self.layout.addWidget(QLabel("To Email Groups:"))
        self.layout.addWidget(self.email_groups_editor)

        # CC Group Editor
        self.cc_groups_editor = QTextEdit()
        self.cc_groups_editor.setPlaceholderText(
            "Enter CC groups with emails (e.g., CCGroup1: cc1@example.com; cc2@example.com)"
        )
        self.layout.addWidget(QLabel("CC Email Groups:"))
        self.layout.addWidget(self.cc_groups_editor)

        # Webhook URL Editor
        self.webhook_url_input = QLineEdit()
        self.webhook_url_input.setPlaceholderText("Enter Webhook URL")
        self.layout.addWidget(QLabel("Webhook URL:"))
        self.layout.addWidget(self.webhook_url_input)

        # Save Button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)
        self.load_settings()

    def save_settings(self):
        """Save updated email groups and webhook URL to the JSON file."""
        try:
            # Parse email groups from the text editor
            email_groups_text = self.email_groups_editor.toPlainText().strip()
            cc_groups_text = self.cc_groups_editor.toPlainText().strip()
            webhook_url = self.webhook_url_input.text().strip()

            # Convert email groups to a dictionary
            email_groups = {}
            if email_groups_text:
                for line in email_groups_text.splitlines():
                    group, emails = line.split(":", 1)
                    email_groups[group.strip()] = [email.strip() for email in emails.split(";")]

            # Convert CC groups to a dictionary
            cc_groups = {}
            if cc_groups_text:
                for line in cc_groups_text.splitlines():
                    group, emails = line.split(":", 1)
                    cc_groups[group.strip()] = [email.strip() for email in emails.split(";")]

            # Prepare the settings to be saved
            mom_settings = {
                "email_groups": email_groups,
                "cc_groups": cc_groups,
                "webhook_url": webhook_url
            }

            # Save to the JSON file
            with open("mom_settings.json", "w") as file:
                json.dump(mom_settings, file, indent=4)

            QMessageBox.information(self, "Success", "Settings saved successfully!")

        except ValueError as ve:
            QMessageBox.warning(self, "Error", f"Invalid input format: {ve}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save settings: {e}")

    def load_settings(self):
        """Load existing settings from the JSON file."""
        try:
            # Check if the settings file exists
            if os.path.exists("mom_settings.json"):
                with open("mom_settings.json", "r") as file:
                    mom_settings = json.load(file)

                # Retrieve email groups, CC groups, and webhook URL
                email_groups = mom_settings.get("email_groups", {})
                cc_groups = mom_settings.get("cc_groups", {})
                webhook_url = mom_settings.get("webhook_url", "")

                # Populate email groups editor
                email_groups_text = "\n".join(
                    f"{group}: {'; '.join(emails)}" for group, emails in email_groups.items()
                )
                self.email_groups_editor.setPlainText(email_groups_text)

                # Populate CC groups editor
                cc_groups_text = "\n".join(
                    f"{group}: {'; '.join(emails)}" for group, emails in cc_groups.items()
                )
                self.cc_groups_editor.setPlainText(cc_groups_text)

                # Populate webhook URL input
                self.webhook_url_input.setText(webhook_url)
            else:
                # If the file does not exist, clear the fields
                self.email_groups_editor.clear()
                self.cc_groups_editor.clear()
                self.webhook_url_input.clear()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load settings: {e}")

