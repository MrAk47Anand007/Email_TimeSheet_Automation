import os
import sqlite3
import json
import requests
import faiss
import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QPushButton, QComboBox, QCheckBox, QCalendarWidget, QTimeEdit,
    QFormLayout, QLineEdit, QLabel, QTextEdit, QHBoxLayout, QMessageBox,QTabWidget
)
from PyQt5.QtCore import QDate, QTime, Qt, QTimer
from Email_and_Timesheet_Automation.SettingWindow import SettingsWindow
from Email_and_Timesheet_Automation.VersionHistory import VersionHistoryWindow
from Email_and_Timesheet_Automation.dbConfig import init_sqlite_db
from Email_and_Timesheet_Automation.htmlGenerator import HtmlGenerator
from Email_and_Timesheet_Automation.momSignature import generate_signature
from Email_and_Timesheet_Automation.mom_setting import MomSettingsWindow


class TaskApp(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = {}
        self.load_settings()
        self.setup_email_scheduler()
        self.conn = init_sqlite_db()
        # Initialize SentenceTransformer model (for task embeddings)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Pre-trained sentence transformer

        # Dynamically set the dimension based on the model's embedding output
        dummy_embedding = self.model.encode(["dummy task"])[0]  # Generate a dummy embedding
        self.dimension = len(dummy_embedding)  # Set dimension dynamically based on embedding size

        # Initialize FAISS index with the determined dimension
        self.index = faiss.IndexFlatL2(self.dimension)

        self.metadata = []  # To store metadata (task data)
        self.setWindowTitle("Task Management")
        self.setGeometry(100, 100, 900, 700)
        self.layout = QVBoxLayout()


        self.initUI()
        self.update_dropdowns()


    def initUI(self):
        # Main layout with tabs
        self.layout = QVBoxLayout()

        # Create Tab Widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Task Management Tab
        self.task_tab = QWidget()
        self.initTaskTab()
        self.tabs.addTab(self.task_tab, "Task Management")

        # MOM Management Tab
        self.mom_tab = QWidget()
        self.initMomManagementTab()
        self.tabs.addTab(self.mom_tab, "MOM Management")

        self.setLayout(self.layout)



    def initTaskTab(self):
        """Initialize the Task Management tab."""
        task_tab_layout = QVBoxLayout(self.task_tab)

        # Create Table for displaying tasks
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(10)
        self.tableWidget.setHorizontalHeaderLabels([
            "Task Name", "Description", "Start Date", "Due Date",
            "Time Spent (hrs)", "Functional Area", "Assignment",
            "Task Type", "Status", "Delete"
        ])
        task_tab_layout.addWidget(self.tableWidget)

        # Add Button for adding tasks
        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_task)
        task_tab_layout.addWidget(self.add_button)

        # Add Automate Button
        self.automate_button = QPushButton("Automate")
        self.automate_button.clicked.connect(self.automate)
        task_tab_layout.addWidget(self.automate_button)

        # Sync with DB Button
        self.sync_button = QPushButton("Sync with DB")
        self.sync_button.clicked.connect(self.sync_with_db)
        task_tab_layout.addWidget(self.sync_button)

        # Settings Button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        task_tab_layout.addWidget(self.settings_button)

        # Version History Button
        self.version_history_button = QPushButton("Version History")
        self.version_history_button.clicked.connect(self.open_version_history)
        task_tab_layout.addWidget(self.version_history_button)

        # Dropdown for selecting a task
        self.task_dropdown = QComboBox()
        self.task_dropdown.addItem("Select a Task")
        self.task_dropdown.currentIndexChanged.connect(self.populate_task_details)
        task_tab_layout.addWidget(self.task_dropdown)

        # Form Layout for Task Input
        self.formLayout = QFormLayout()
        self.task_name_input = QLineEdit()
        self.formLayout.addRow("Task Name:", self.task_name_input)

        self.description_input = QTextEdit()
        self.formLayout.addRow("Description:", self.description_input)

        self.todays_target = QLineEdit()
        self.formLayout.addRow("Today's Target:", self.todays_target)

        # Start Date Widget
        self.start_date_input = self.create_date_widget()
        self.formLayout.addRow("Start Date:", self.start_date_input)

        # Due Date Widget
        self.due_date_input = self.create_date_widget()
        self.formLayout.addRow("Due Date:", self.due_date_input)

        # Time Spent Widget
        self.time_spent_input = QTimeEdit(QTime(0, 0))
        self.time_spent_input.setDisplayFormat("HH:mm")
        self.formLayout.addRow("Time Spent (HH:mm):", self.time_spent_input)

        # Other Form Fields
        self.functional_area_input = QComboBox()
        self.functional_area_input.addItems(["Development", "Testing", "Design", "Research", "Training"])
        self.formLayout.addRow("Functional Area:", self.functional_area_input)

        self.assignment_input = QComboBox()
        self.assignment_input.addItems(["Research", "Task", "Training", "Development"])
        self.formLayout.addRow("Assignment:", self.assignment_input)

        self.task_type_input = QComboBox()
        self.task_type_input.addItems(["Bug Fix", "Feature", "Research"])
        self.formLayout.addRow("Task Type:", self.task_type_input)

        self.status_checkbox = QCheckBox("Completed")
        self.formLayout.addRow("Status:", self.status_checkbox)

        self.mom_completed = QLineEdit()
        self.formLayout.addRow("Mom Completed Percentage:", self.mom_completed)

        task_tab_layout.addLayout(self.formLayout)

    def initMomManagementTab(self):
        """Initialize the MOM Management tab."""
        mom_tab_layout = QVBoxLayout(self.mom_tab)

        # Form for MOM Inputs
        mom_form_layout = QFormLayout()

        # Dropdown for selecting previous MOM records
        self.previous_mom_dropdown = QComboBox()
        self.previous_mom_dropdown.addItem("Select Previous MOM")
        self.previous_mom_dropdown.currentIndexChanged.connect(self.populate_mom_data)
        mom_form_layout.addRow("Previous MOM:", self.previous_mom_dropdown)

        # Dropdown for selecting email groups
        self.email_group_dropdown = QComboBox()
        self.email_group_dropdown.addItem("Select Group")
        self.email_group_dropdown.currentIndexChanged.connect(self.populate_emails)
        mom_form_layout.addRow("Email Group:", self.email_group_dropdown)

        # To Email Input (text box)
        self.to_input = QTextEdit()
        mom_form_layout.addRow("To:", self.to_input)

        # CC Email Dropdown (populated from settings)
        self.cc_dropdown = QComboBox()
        self.cc_dropdown.addItem("Select CC Group")
        self.cc_dropdown.currentIndexChanged.connect(self.populate_cc_emails)
        mom_form_layout.addRow("CC Group:", self.cc_dropdown)

        # CC Input Text Box
        self.cc_input = QTextEdit()
        mom_form_layout.addRow("CC:", self.cc_input)

        # MOM Leader Input
        self.mom_leader_input = QLineEdit()
        mom_form_layout.addRow("MOM Leader:", self.mom_leader_input)

        # MOM Creator Input
        self.mom_creator_input = QLineEdit()
        mom_form_layout.addRow("MOM Creator:", self.mom_creator_input)

        # Present Members Input
        self.present_input = QTextEdit()
        mom_form_layout.addRow("Present Members:", self.present_input)

        # Absent Members Input
        self.absent_input = QTextEdit()
        mom_form_layout.addRow("Absent Members:", self.absent_input)



        mom_tab_layout.addLayout(mom_form_layout)

        # Buttons for MOM actions
        button_layout = QHBoxLayout()

        self.save_mom_button = QPushButton("Save")
        self.save_mom_button.clicked.connect(self.save_mom_data)
        button_layout.addWidget(self.save_mom_button)

        self.automate_mom_button = QPushButton("Automate")
        self.automate_mom_button.clicked.connect(self.automate_mom)
        button_layout.addWidget(self.automate_mom_button)

        # Settings Button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_mom_settings)
        button_layout.addWidget(self.settings_button)

        mom_tab_layout.addLayout(button_layout)

        # Load email groups and CC into the dropdowns
        self.refresh_mom_dropdowns()
        self.load_previous_mom_data()

    def load_email_groups(self):
        """Load email groups from settings."""
        try:
            # Load settings from the file
            with open("mom_settings.json", "r") as file:
                mom_settings = json.load(file)
                email_groups = mom_settings.get("email_groups", {})  # Get the email addresses

                # Populate the email group dropdown
                self.email_group_dropdown.addItem("Select Group")  # Default option
                for group_name in email_groups:
                    self.email_group_dropdown.addItem(group_name)  # Add group name to the dropdown

        except FileNotFoundError:
            print("MOM settings file not found.")
        except Exception as e:
            print(f"Error loading email groups: {str(e)}")

    def load_previous_mom_data(self):
        """Load previous MOM data from the database into the dropdown."""
        try:
            # Connect to SQLite database
            conn = sqlite3.connect("mom_management.db")
            cursor = conn.cursor()

            # Query the database for all MOM records
            cursor.execute("SELECT id, timestamp FROM mom_data ORDER BY timestamp DESC")
            mom_records = cursor.fetchall()

            # Populate the dropdown with the retrieved MOM records
            self.previous_mom_dropdown.clear()
            self.previous_mom_dropdown.addItem("Select Previous MOM")  # Default option
            for record in mom_records:
                mom_id, timestamp = record
                self.previous_mom_dropdown.addItem(f"MOM ID: {mom_id} - {timestamp}")

            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load previous MOM data: {e}")

    def populate_mom_data(self):
        """Populate the text fields with the data of the selected previous MOM."""
        selected_mom_index = self.previous_mom_dropdown.currentIndex()
        print("ak",selected_mom_index)
        if selected_mom_index <= 0:  # No MOM selected
            return

        try:
            # Connect to SQLite database
            conn = sqlite3.connect("mom_management.db")
            cursor = conn.cursor()

            # Get the MOM ID from the selected item
            selected_mom_id = self.previous_mom_dropdown.currentText().split(" - ")[0].split(": ")[1]

            # Query the database for the selected MOM data
            cursor.execute(
                "SELECT to_emails, cc_emails, mom_leader, mom_creator, present_members,absent_members FROM mom_data WHERE id = ?",
                (selected_mom_id,))
            mom_record = cursor.fetchone()

            if mom_record:
                to_emails, cc_emails, mom_leader, mom_creator,present_members, absent_members = mom_record

                # Populate the fields with the retrieved data
                self.to_input.setPlainText(to_emails)
                self.mom_leader_input.setText(mom_leader)
                self.mom_creator_input.setText(mom_creator)
                self.present_input.setPlainText(present_members)
                self.absent_input.setPlainText(absent_members)
                self.cc_input.setPlainText(cc_emails)


            else:
                QMessageBox.warning(self, "Error", "No data found for the selected MOM.")

            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to populate MOM data: {e}")

    def load_cc_emails(self):
        """Load CC emails into the dropdown from settings."""
        try:
            # Load settings from the mom_settings.json file
            with open("mom_settings.json", "r") as file:
                mom_settings = json.load(file)
                email_groups = mom_settings.get("email_groups", {})  # Get the email groups

                # Populate CC dropdown with grouped emails
                self.cc_dropdown.clear()  # Clear previous CC emails
                for group_name, emails in email_groups.items():
                    self.cc_dropdown.addItem(group_name)  # Add group as a category
                    for email in emails:
                        self.cc_dropdown.addItem(f"  {email}")  # Indented emails under the group

        except FileNotFoundError:
            print("MOM settings file not found.")
        except Exception as e:
            print(f"Error loading CC emails: {str(e)}")



    def populate_cc_emails(self):
        """Populate the To field based on the selected email group."""
        selected_group = self.cc_dropdown.currentText()
        if selected_group == "Select CC Group":
            self.cc_input.clear()
            return  # No group selected

        try:
            with open("mom_settings.json", "r") as file:
                mom_settings = json.load(file)
                email_groups = mom_settings.get("cc_groups", {})

                # Populate "To" field with emails from the selected group
                emails = email_groups.get(selected_group, [])
                self.cc_input.setPlainText("; ".join(emails))  # Display emails in the To input field

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to populate emails: {e}")

    def populate_emails(self):
        """Populate the To field based on the selected email group."""
        selected_group = self.email_group_dropdown.currentText()
        if selected_group == "Select Group":
            self.to_input.clear()
            return  # No group selected

        try:
            with open("mom_settings.json", "r") as file:
                mom_settings = json.load(file)
                email_groups = mom_settings.get("email_groups", {})

                # Populate "To" field with emails from the selected group
                emails = email_groups.get(selected_group, [])
                self.to_input.setPlainText("; ".join(emails))  # Display emails in the To input field

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to populate emails: {e}")

    def refresh_mom_dropdowns(self):
        """Refresh the Email Group and CC dropdowns based on the updated settings."""
        try:
            with open("mom_settings.json", "r") as file:
                mom_settings = json.load(file)
                email_groups = mom_settings.get("email_groups", {})
                cc_groups = mom_settings.get("cc_groups", {})

                # Update Email Group Dropdown
                self.email_group_dropdown.clear()
                self.email_group_dropdown.addItem("Select Group")
                self.email_group_dropdown.addItems(email_groups.keys())

                # Update CC Dropdown
                self.cc_dropdown.clear()
                self.cc_dropdown.addItem("Select CC Group")
                self.cc_dropdown.addItems(cc_groups.keys())

        except FileNotFoundError:
            QMessageBox.warning(self, "Error", "Settings file not found. Unable to refresh dropdowns.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to refresh dropdowns: {e}")

    def save_mom_data(self):
        """Save MOM data to an SQLite database."""
        # Collect the MOM data from the input fields
        to_emails = "; ".join(self.to_input.toPlainText().splitlines())  # Join emails as a single string
        cc_emails = self.cc_input.toPlainText().strip()  # Get CC emails from cc_input
        if not cc_emails:  # If no CC emails are entered, check the dropdown
            cc_emails = "; ".join([self.cc_dropdown.itemText(i) for i in range(self.cc_dropdown.count()) if
                                   "  " in self.cc_dropdown.itemText(
                                       i)])  # Join CC emails from dropdown if cc_input is empty
        mom_leader = self.mom_leader_input.text()
        mom_creator = self.mom_creator_input.text()
        present_member = "; ".join(
            self.present_input.toPlainText().splitlines())  # Join absent members as a single string
        absent_members = "; ".join(
            self.absent_input.toPlainText().splitlines())  # Join absent members as a single string

        mom_data = {
            "to": to_emails,
            "cc": cc_emails,
            "mom_leader": mom_leader,
            "mom_creator": mom_creator,
            "present": present_member,
            "absent": absent_members
        }

        try:
            # Connect to SQLite database (or create it if it doesn't exist)
            conn = sqlite3.connect("mom_management.db")
            cursor = conn.cursor()

            # Create the MOM table if it doesn't already exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mom_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    to_emails TEXT,
                    cc_emails TEXT,
                    mom_leader TEXT,
                    mom_creator TEXT,
                    present_members TEXT,
                    absent_members TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Insert the collected MOM data into the table
            cursor.execute("""
                INSERT INTO mom_data (to_emails, cc_emails, mom_leader, mom_creator, present_members,absent_members)
                VALUES (:to, :cc, :mom_leader, :mom_creator,:present, :absent)
            """, mom_data)

            # Commit the transaction and close the connection
            conn.commit()
            conn.close()

            # Refresh the previous MOM dropdown with the newly saved data
            self.refresh_previous_mom_dropdown()

            QMessageBox.information(self, "Success", "MOM data saved successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save MOM data: {str(e)}")

    def open_mom_settings(self):
        """Open the MOM Settings window and refresh dropdowns after saving."""
        self.settings_window = MomSettingsWindow(self)
        self.settings_window.exec_()  # Show settings as a modal dialog
        self.refresh_mom_dropdowns()  # Refresh dropdowns after closing settings

    def automate_mom(self):
        """
        Automate the process by formatting MOM data into JSON and calling the webhook.
        """
        to_emails = "; ".join(self.to_input.toPlainText().splitlines())  # Join emails as a single string
        cc_emails = self.cc_input.toPlainText().strip()
        if not cc_emails:  # If no CC emails are entered, check the dropdown
            cc_emails = "; ".join([self.cc_dropdown.itemText(i) for i in range(self.cc_dropdown.count()) if
                                   "  " in self.cc_dropdown.itemText(i)])
        mom_leader = self.mom_leader_input.text()
        mom_creator = self.mom_creator_input.text()
        present_member = "; ".join(self.present_input.toPlainText().splitlines())
        absent_members_pre = self.absent_input.toPlainText()
        absent_members = ", ".join([member.strip() for member in absent_members_pre.splitlines()])

        # Step 4: Prepare the final JSON data
        mom_data = {
            "to": to_emails,
            "cc": cc_emails,
            "mom_leader": mom_leader,
            "mom_creator": mom_creator,
            "present": present_member,
            "absent": absent_members,
            "signature": generate_signature()
        }

        # Convert the dictionary to a JSON string
        json_data = json.dumps(mom_data)

        try:
            # Load settings from the mom_settings.json file to retrieve the webhook URL
            with open("mom_settings.json", "r") as file:
                mom_settings = json.load(file)
                webhook_url = mom_settings.get("webhook_url", "").strip()

            if not webhook_url:
                QMessageBox.warning(self, "Error", "Webhook URL is not set in the settings.")
                return

            # Send the JSON data to the webhook
            response = requests.post(webhook_url, json=mom_data)

            # Check if the request was successful
            if response.status_code == 202:
                QMessageBox.information(self, "Success", "MOM data sent to webhook successfully.")
            else:
                QMessageBox.warning(self, "Error",
                                    f"Failed to send data to webhook. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "Error", f"An error occurred while sending data to the webhook: {e}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to retrieve webhook URL or send data: {e}")

    def refresh_previous_mom_dropdown(self):
        """Refresh the Previous MOM dropdown with the latest data from the database."""
        try:
            # Connect to SQLite database
            conn = sqlite3.connect("mom_management.db")
            cursor = conn.cursor()

            # Query the database for all MOM records
            cursor.execute("SELECT id, timestamp FROM mom_data ORDER BY timestamp DESC")
            mom_records = cursor.fetchall()

            # Populate the dropdown with the retrieved MOM records
            self.previous_mom_dropdown.clear()
            self.previous_mom_dropdown.addItem("Select Previous MOM")  # Default option
            for record in mom_records:
                mom_id, timestamp = record
                self.previous_mom_dropdown.addItem(f"MOM ID: {mom_id} - {timestamp}")

            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to refresh Previous MOM dropdown: {e}")

    def setup_email_scheduler(self):
        schedule_time = QTime.fromString(self.settings["schedule_time"], "HH:mm")
        now = QTime.currentTime()
        seconds_until_trigger = now.secsTo(schedule_time)
        if seconds_until_trigger < 0:  # If time has passed for today
            seconds_until_trigger += 24 * 3600  # Schedule for tomorrow

        self.email_timer = QTimer(self)
        self.email_timer.setSingleShot(True)
        self.email_timer.timeout.connect(self.automate)  # Replace with your email logic
        self.email_timer.start(seconds_until_trigger * 1000)


    def load_settings(self):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "../settings.json")


        try:
            # Use the resolved path
            with open(config_path, "r") as config_file:
                self.settings= json.load(config_file)
        except FileNotFoundError:
            self.settings = {
                "functional_areas": ["Development", "Testing", "Design"],
                "assignments": ["Research", "Task", "Training", "Development"],
                "task_types": ["Bug Fix", "Feature", "Research"],
                "schedule_time": "09:00",
                "webhook_url": "",
                "to_user": [],
                "cc_user": [],
                "role":"",
                "email":"",
                "name":"",
                "mobileNo":"",
                "timesheet_link":""
            }

    def update_dropdowns(self):
        self.functional_area_input.clear()
        self.functional_area_input.addItems(self.settings.get("functional_areas", []))

        self.assignment_input.clear()
        self.assignment_input.addItems(self.settings.get("assignments", []))

        self.task_type_input.clear()
        self.task_type_input.addItems(self.settings.get("task_types", []))

    def create_date_widget(self):
        """
        Creates a custom date selector with a line edit and calendar popup.
        """
        container = QWidget()
        layout = QHBoxLayout(container)

        date_line_edit = QLineEdit()
        date_line_edit.setPlaceholderText("Select Date")
        date_line_edit.setReadOnly(True)

        calendar = QCalendarWidget()
        calendar.hide()

        def show_calendar():
            calendar.show()

        def select_date():
            selected_date = calendar.selectedDate()
            date_line_edit.setText(selected_date.toString("yyyy-MM-dd"))
            calendar.hide()

        date_line_edit.mousePressEvent = lambda _: show_calendar()
        calendar.clicked.connect(select_date)

        layout.addWidget(date_line_edit)
        layout.addWidget(calendar)
        return container

    def add_task(self):
        # Collect data from the UI
        task_name = self.task_name_input.text()
        description = self.description_input.toPlainText()
        start_date = self.start_date_input.findChild(QLineEdit).text()
        due_date = self.due_date_input.findChild(QLineEdit).text()

        # Validate input
        if not task_name or not start_date or not due_date:
            QMessageBox.warning(self, "Validation Error", "Task Name, Start Date, and Due Date are required.")
            return

        # Insert new task into the main tasks table (SQL)
        cursor = self.conn.cursor()
        cursor.execute(""" 
            INSERT INTO tasks (task_name, description, start_date, due_date, time_spent, functional_area, assignment, task_type, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) 
        """, (
            task_name,
            description,
            start_date,
            due_date,
            self.time_spent_input.text(),
            self.functional_area_input.currentText(),
            self.assignment_input.currentText(),
            self.task_type_input.currentText(),
            "Completed" if self.status_checkbox.isChecked() else "Pending"
        ))

        task_id = cursor.lastrowid  # Get the ID of the inserted task

        # Add a version entry for the task (Task versioning)
        version_data = {
            "task_name": task_name,
            "description": description,
            "start_date": start_date,
            "due_date": due_date,
            "time_spent": self.time_spent_input.text(),
            "functional_area": self.functional_area_input.currentText(),
            "assignment": self.assignment_input.currentText(),
            "task_type": self.task_type_input.currentText(),
            "status": "Completed" if self.status_checkbox.isChecked() else "Pending"
        }
        cursor.execute(""" 
            INSERT INTO task_versions (task_id, task_name, version_date, version_data) 
            VALUES (?, ?, ?, ?) 
        """, (
            task_id,
            task_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            json.dumps(version_data)
        ))

        self.conn.commit()

        # Generate task embedding using SentenceTransformer
        task_text = f"{task_name} {description} {start_date} {due_date}"
        task_embedding = self.model.encode([task_text])[0]  # Embedding for the task (single vector)

        # Validate embedding size matches FAISS index dimension
        if len(task_embedding) != self.index.d:
            raise ValueError(f"Embedding dimension mismatch: Expected {self.index.d}, got {len(task_embedding)}")

        # Add the task embedding to FAISS
        self.index.add(np.array([task_embedding]))

        # Store metadata for the task
        self.metadata.append({
            "id": task_id,
            "task_data": version_data
        })

        # Add task to the UI table
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)

        # Assuming column 0 is for task_id (hidden), and subsequent columns are for task data
        self.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(task_id)))  # Task ID (hidden column)
        for i, key in enumerate(version_data.keys(), start=1):  # Start from column 1
            self.tableWidget.setItem(row_position, i, QTableWidgetItem(str(version_data[key])))

        # Hide the task_id column (if it's not meant to be visible)
        self.tableWidget.setColumnHidden(0, True)

        # Add Delete button
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_task(task_id))
        self.tableWidget.setCellWidget(row_position, len(version_data), delete_button)

        # Clear inputs after adding the task
        self.clear_task_inputs()

        QMessageBox.information(self, "Success", "Task has been added successfully.")

    def automate(self):
        # Collect all tasks from the table
        tasks_data = []
        for row in range(self.tableWidget.rowCount()):
            task_data = {}
            for col in range(self.tableWidget.columnCount() - 1):  # Excluding 'Delete' column
                header = self.tableWidget.horizontalHeaderItem(col).text()
                task_data[header] = self.tableWidget.item(row, col).text()
            tasks_data.append(task_data)

        # Generate HTML content for the collected tasks
        tasks_list = [{"Task Name": task["Task Name"], "Task Keyword": task["Description"],
                       "Time Spent (hrs)": task["Time Spent (hrs)"]} for task in tasks_data]

        class TaskCollection:
            date = datetime.now()

            def to_dict(self):
                return {"Tasks": tasks_list}

        # Generate the HTML for all tasks
        task_collection = TaskCollection()
        html_content = HtmlGenerator.generate_task_table(task_collection)

        # Create the final JSON object containing the HTML content and task data
        json_object = {
            "htmlContent": html_content,
            "tasks": tasks_data,
            "to_user": self.settings.get("to_user", []),
            "cc_user": self.settings.get("cc_user", []),
            "mom_completed": self.mom_completed.text(),
            "todays_target": self.todays_target.text()
        }

        formatted_json_object = json.dumps(json_object, indent=4)
        self.webhookcaller(formatted_json_object)
        print(formatted_json_object)

        # Display the HTML content (can be used to save, print, or display)
        QMessageBox.information(self, "Generated HTML", html_content)



    def view_version_history(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT version_date, version_data FROM task_versions WHERE task_id = ?
        """, (task_id,))
        versions = cursor.fetchall()

        history_text = "\n".join([
            f"Version Date: {version[0]}\nDetails: {version[1]}\n" for version in versions
        ])

        QMessageBox.information(self, "Version History", history_text)



    def open_version_history(self):
        self.version_history_window = VersionHistoryWindow(parent=self, conn=self.conn)
        self.version_history_window.show()

    def delete_task(self, task_id):
        """
        Deletes a task from the FAISS index, metadata, SQLite database, and the UI by task_id.
        :param task_id: The unique task ID to delete
        """
        # Locate the task in the metadata list
        task_idx = next((idx for idx, task in enumerate(self.metadata) if task["id"] == task_id), None)

        if task_idx is None:
            QMessageBox.warning(self, "Error", f"Task with ID {task_id} not found.")
            return

        try:
            # Begin SQLite deletion
            cursor = self.conn.cursor()

            # Delete task from the `tasks` table
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.conn.commit()
            print(f"Task with ID {task_id} deleted from SQLite.")

            # Remove metadata entry
            self.metadata.pop(task_idx)

            # Remove task from the UI table
            for row in range(self.tableWidget.rowCount()):
                # Assuming task_id is stored in the first (hidden) column
                table_task_id = self.tableWidget.item(row, 0).text()
                if str(task_id) == table_task_id:  # Match task_id as string
                    self.tableWidget.removeRow(row)
                    print(f"Task with ID {task_id} removed from the UI table.")
                    break

            # Rebuild the FAISS index
            self.rebuild_faiss_index()

            print(f"Task with ID {task_id} deleted from FAISS.")
            QMessageBox.information(self, "Success", f"Task with ID {task_id} has been deleted successfully.")

        except Exception as e:
            print(f"Error deleting task with ID {task_id}: {e}")
            QMessageBox.warning(self, "Error", f"Failed to delete task with ID {task_id}.")

    def search_task_with_faiss(self, query_embedding, k=5):
        """
        Search for similar tasks based on query embedding.
        query_embedding: A numpy array representing the query vector
        k: Number of similar results to return
        """
        # Perform the search
        distances, indices = self.index.search(np.array([query_embedding]), k)

        results = []
        for idx in indices[0]:
            task = self.metadata[idx]
            results.append(task)

        return results

    def open_settings(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.settings_updated.connect(self.refresh_settings)  # Connect the signal
        self.settings_window.show()

    def rebuild_faiss_index(self):
        """
        Rebuilds the FAISS index using the current metadata.
        """
        try:
            # Reinitialize the FAISS index
            self.index = faiss.IndexFlatL2(self.dimension)
            new_embeddings = []

            # Extract embeddings from metadata
            for task in self.metadata:
                task_data = task["task_data"]  # Assuming embeddings are stored in task_data
                embedding = task_data.get("embedding")  # Adjust based on actual metadata structure
                if embedding:
                    new_embeddings.append(np.array(embedding))

            # Add the embeddings back to the index
            if new_embeddings:
                self.index.add(np.vstack(new_embeddings))  # Stack and add embeddings

            print("FAISS index rebuilt successfully.")

        except Exception as e:
            print(f"Error rebuilding FAISS index: {e}")

    def refresh_settings(self):
        self.load_settings()  # Reload the settings from the configuration file
        self.update_dropdowns()  # Update dropdowns based on new settings

    def sync_with_db(self):
        cursor = self.conn.cursor()

        # Get today's date
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Query the task_versions table for tasks created today
        cursor.execute("""
            SELECT DISTINCT task_id, task_name, version_date 
            FROM task_versions
            WHERE DATE(version_date) = ?
            ORDER BY version_date ASC
        """, (current_date,))
        tasks = cursor.fetchall()

        # If no tasks for today, look for the most recent earlier date
        if not tasks:
            cursor.execute("""
                SELECT DISTINCT DATE(version_date) AS previous_date
                FROM task_versions
                WHERE version_date < ?
                ORDER BY version_date DESC
                LIMIT 1
            """, (current_date,))
            previous_date_row = cursor.fetchone()

            if previous_date_row:
                previous_date = previous_date_row[0]
                QMessageBox.information(self, "No Tasks for Today",
                                        f"No tasks found for today. Displaying tasks from {previous_date}.")

                # Fetch tasks for the most recent earlier date
                cursor.execute("""
                    SELECT DISTINCT task_id, task_name, version_date 
                    FROM task_versions
                    WHERE DATE(version_date) = ?
                    ORDER BY version_date ASC
                """, (previous_date,))
                tasks = cursor.fetchall()
            else:
                # No earlier data available
                QMessageBox.information(self, "No Tasks", "No tasks found in the database!")
                return

        # Clear existing items and populate dropdown
        self.task_dropdown.clear()
        self.task_dropdown.addItem("Select a Task")
        for task_id, task_name, version_date in tasks:
            display_name = f"{task_name} ({version_date})"
            self.task_dropdown.addItem(display_name, task_id)

    def populate_task_details(self):
        # Get the selected task ID
        selected_task_id = self.task_dropdown.currentData()

        if selected_task_id is None:
            return  # No valid task selected

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT task_name, version_data, version_date 
            FROM task_versions 
            WHERE task_id = ? 
            ORDER BY version_date DESC 
            LIMIT 1
        """, (selected_task_id,))
        task_version = cursor.fetchone()

        if task_version:
            task_name, version_data, version_date = task_version
            task_details = json.loads(version_data)  # Deserialize version_data JSON

            # Populate UI fields with task details
            self.task_name_input.setText(task_details.get("task_name", ""))
            self.description_input.setPlainText(task_details.get("description", ""))
            self.start_date_input.findChild(QLineEdit).setText(task_details.get("start_date", ""))
            self.due_date_input.findChild(QLineEdit).setText(task_details.get("due_date", ""))

            time_string = task_details.get("time_spent", "00:00")
            time_obj = QTime.fromString(time_string, 'HH:mm')
            self.time_spent_input.setTime(time_obj)

            self.functional_area_input.setCurrentText(task_details.get("functional_area", ""))
            self.assignment_input.setCurrentText(task_details.get("assignment", ""))
            self.task_type_input.setCurrentText(task_details.get("task_type", ""))
            self.status_checkbox.setChecked(task_details.get("status") == "Completed")
        else:
            QMessageBox.warning(self, "Error", "Task details not found!")

    def clear_task_inputs(self):
        """
        Clears all input fields to reset the task form.
        """
        self.task_name_input.clear()  # Clear text in the task name field
        self.description_input.clear()  # Clear the description text area
        self.start_date_input.findChild(QLineEdit).clear()  # Clear the start date
        self.due_date_input.findChild(QLineEdit).clear()  # Clear the due date
        self.time_spent_input.setTime(QTime(0, 0))  # Reset the time spent to 00:00
        self.functional_area_input.setCurrentIndex(0)  # Reset functional area dropdown to the first item
        self.assignment_input.setCurrentIndex(0)  # Reset assignment dropdown to the first item
        self.task_type_input.setCurrentIndex(0)  # Reset task type dropdown to the first item
        self.status_checkbox.setChecked(False)  # Uncheck the status checkbox




    def webhookcaller(self, task_json):
        url = self.settings.get("webhook_url", "")
        if not url:
            QMessageBox.warning(self, "Error", "Webhook URL is not configured.")
            return

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=task_json, headers=headers)

        if response.status_code == 202:
            QMessageBox.information(self, "Success", "Webhook called successfully.")
        else:
            QMessageBox.warning(self, "Error", f"Webhook call failed: {response.status_code}")


if __name__ == '__main__':
    app = QApplication([])
    window = TaskApp()
    window.show()
    app.exec_()
