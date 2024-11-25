import sys
from PyQt5.QtWidgets import QApplication
from Email_and_Timesheet_Automation.TaskApp import TaskApp  # Import the TaskApp class from TaskApp


def main():
    """
    Main entry point for the Task Management application.
    Initializes and runs the TaskApp.
    """
    app = QApplication(sys.argv)  # Create a QApplication instance
    task_app = TaskApp()          # Initialize the TaskApp from TaskApp
    task_app.show()               # Show the main application window
    sys.exit(app.exec_())         # Start the Qt event loop


if __name__ == "__main__":
    main()
