from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QPushButton, QComboBox, QCheckBox, QCalendarWidget, QTimeEdit,
    QFormLayout, QLineEdit, QLabel, QTextEdit, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QDate, QTime, Qt, QTimer

from Email_and_Timesheet_Automation.SettingWindow import SettingsWindow
from Email_and_Timesheet_Automation.VersionHistory import VersionHistoryWindow
from Email_and_Timesheet_Automation.dbConfig import init_sqlite_db, init_chromadb
from Email_and_Timesheet_Automation.htmlGenerator import HtmlGenerator
import json
import requests




class TaskApp(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = {}
        self.load_settings()
        self.setup_email_scheduler()
        self.conn = init_sqlite_db()
        self.chromadb = init_chromadb()

        self.setWindowTitle("Task Management")
        self.setGeometry(100, 100, 900, 700)
        self.layout = QVBoxLayout()

        self.initUI()
        self.update_dropdowns()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Create Table for displaying tasks
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(10)
        self.tableWidget.setHorizontalHeaderLabels([
            "Task Name", "Description", "Start Date", "Due Date",
            "Time Spent (hrs)", "Functional Area", "Assignment",
            "Task Type", "Status", "Delete"
        ])
        self.layout.addWidget(self.tableWidget)

        # Add Button for adding tasks
        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_task)
        self.layout.addWidget(self.add_button)



        # Add Automate Button
        self.automate_button = QPushButton("Automate")
        self.automate_button.clicked.connect(self.automate)
        self.layout.addWidget(self.automate_button)

        self.setLayout(self.layout)

        # Add Sync with DB Button
        self.sync_button = QPushButton("Sync with DB")
        self.sync_button.clicked.connect(self.sync_with_db)
        self.layout.addWidget(self.sync_button)


        # add settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        self.layout.addWidget(self.settings_button)

        # version history button
        self.version_history_button = QPushButton("Version History")
        self.version_history_button.clicked.connect(self.open_version_history)
        self.layout.addWidget(self.version_history_button)

        self.task_dropdown = QComboBox()
        self.task_dropdown.addItem("Select a Task")
        self.task_dropdown.currentIndexChanged.connect(self.populate_task_details)
        self.layout.addWidget(self.task_dropdown)

        # Layout for task input
        self.formLayout = QFormLayout()
        self.task_name_input = QLineEdit()
        self.formLayout.addRow("Task Name:", self.task_name_input)

        self.description_input = QTextEdit()
        self.formLayout.addRow("Description:", self.description_input)

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

        self.layout.addLayout(self.formLayout)
        self.setLayout(self.layout)

    def load_settings(self):
        try:
            with open("./Email_and_Timesheet_Automation/settings.json", "r") as config_file:
                self.settings = json.load(config_file)
        except FileNotFoundError:
            self.settings = {
                "functional_areas": ["Development", "Testing", "Design"],
                "assignments": ["Research", "Task", "Training", "Development"],
                "task_types": ["Bug Fix", "Feature", "Research"],
                "schedule_time": "09:00",
                "webhook_url": "",
                "to_user": [],
                "cc_user": []
            }

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

        # Insert new task into the main tasks table
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

        # Add a version entry for the task
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

        # Add task to the UI table
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)
        for i, key in enumerate(version_data.keys()):
            self.tableWidget.setItem(row_position, i, QTableWidgetItem(str(version_data[key])))

        # Add Delete button
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_task(row_position))
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
            "cc_user": self.settings.get("cc_user", [])
        }

        formatted_json_object = json.dumps(json_object, indent=4)
        self.webhookcaller(formatted_json_object)
        print(formatted_json_object)

        # Display the HTML content (can be used to save, print, or display)
        QMessageBox.information(self, "Generated HTML", html_content)

    def add_task_to_sqlite(self, task_data):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (task_name, description, start_date, due_date, time_spent,
                               functional_area, assignment, task_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_data["task_name"], task_data["description"], task_data["start_date"],
            task_data["due_date"], task_data["time_spent"], task_data["functional_area"],
            task_data["assignment"], task_data["task_type"], task_data["status"]
        ))
        self.conn.commit()

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

    def add_task_to_chromadb(self, task_data):
        # Convert data to JSON and add to ChromaDB
        task_id = str(self.tableWidget.rowCount() + 1)  # Unique ID
        task_json = json.dumps(task_data)
        self.chromadb.add(
            ids=[task_id],
            documents=[task_json],
            metadatas=[task_data]
        )

    def open_version_history(self):
        self.version_history_window = VersionHistoryWindow(parent=self, conn=self.conn)
        self.version_history_window.show()

    def delete_task(self, row):
        task_name = self.tableWidget.item(row, 0).text()  # Assuming the first column is the task name
        self.remove_task_from_sqlite(task_name)
        self.remove_task_from_chromadb(task_name)
        self.tableWidget.removeRow(row)

    def open_settings(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.settings_updated.connect(self.refresh_settings)  # Connect the signal
        self.settings_window.show()

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

    def remove_task_from_sqlite(self, task_name):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM tasks WHERE task_name = ?", (task_name,))
            self.conn.commit()
        except Exception as e:
            print(f"Error removing task from SQLite: {e}")

    def remove_task_from_chromadb(self, task_name):
        try:
            # Assuming metadata contains a 'task_name' field
            ids_to_remove = self.chromadb.get(
                where={"task_name": task_name}
            ).get("ids", [])

            if ids_to_remove:
                self.chromadb.delete(ids=ids_to_remove)
            else:
                print(f"No matching tasks found in ChromaDB for task name: {task_name}")
        except Exception as e:
            print(f"Error removing task from ChromaDB: {e}")

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
