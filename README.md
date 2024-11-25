# Email TimeSheet Automation

This project automates the generation and sending of timesheets via email, designed to help streamline the reporting process for employees. It retrieves task details from a database or external source, generates a timesheet report, and emails it to the specified recipients. The automation is intended to save time, reduce errors, and ensure timely reporting.

## Features

- **Automatic Timesheet Generation:** Automatically generates daily or weekly timesheet reports based on the user's work data.
- **Email Integration:** Sends the generated timesheet as an email attachment to predefined recipients.
- **Database Integration:** Pulls task details from a database (ChromaDB/SQLite) to populate the timesheet.
- **Real-Time Task Tracking:** Tracks work hours and logs data for accurate timesheet generation.
- **User-Friendly Interface:** Provides an easy-to-use interface for configuring email and timesheet options.

## Requirements

- Python 3.x
- Libraries:
  - `smtplib` (for email sending)
  - `sqlite3` or `ChromaDB` (for task data)
  - `datetime` (for handling dates)
  - Any other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/MrAk47Anand007/Email_TimeSheet_Automation.git
   cd Email_TimeSheet_Automation
