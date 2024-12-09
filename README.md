# Daily Status Email & Timesheet Automation

This project is designed to automate the daily status email and timesheet reporting process, saving time and reducing manual effort. It leverages Python for automation, Power Automate for webhook integration, and PyQt5 for a user-friendly application interface.

---

## Features

### 1. **Task Management**
   - **Dashboard:** Add and manage tasks via a user-friendly PyQt5 interface.
   - **SQLite Integration:** Tasks are stored in a database for future reuse.
   - **Reuse Tasks:** Sync tasks from the database and populate fields automatically, allowing quick edits and additions.

### 2. **Email and Timesheet Automation**
   - **Power Automate Webhook:** Automates email sending and Microsoft 365 timesheet updates in one click.
   - **Customizable Fields:** Configure functional areas, task types, task areas, webhook URL, and personal information (e.g., email signature) in settings.

### 3. **MoM (Minutes of Meeting) Automation**
   - Manage attendance (present/absent) and MoM details in the app.
   - Generate and send MoM emails using predefined email settings, ensuring consistency and reusability.

### 4. **Future Scope**
   - **AI/ML Integration:** Leverages a vector database (FAISS) to train models for:
     - Automatically generating email drafts based on keywords.
     - Using a user tracking system to generate detailed activity reports in JSON for training or contextual data.
   - **User Tracking System:** Collects daily user activity data to support advanced email automation and reporting.

---

## Getting Started

### Prerequisites
- Python 3.8 or later
- Microsoft 365 account
- Power Automate for webhook integration

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Email_Timesheet_Automation.git
   cd Email_Timesheet_Automation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

---

## Usage

### Task Management
1. **Add Tasks:**
   - Use the dashboard to add tasks with necessary details.
   - Save tasks to the SQLite database for future reference.

2. **Reuse Tasks:**
   - Click "Sync with DB" to fetch reusable tasks into a dropdown.
   - Select a task, make minor edits if needed, and click "Add Task."

3. **Automate Process:**
   - After adding tasks, click "Automate" to:
     - Collect task data.
     - Send the data to Power Automate webhook.
     - Process email sending and timesheet updates automatically.

### MoM Automation
1. Open the `MoM_Management` tab in the app.
2. Add details for:
   - Attendance (present/absent).
   - Lead and creator roles.
3. Generate and send MoM emails with preconfigured CC and recipient details.

### Settings
- Configure once and reuse:
  - Functional areas, task types, task areas.
  - Webhook URL for automation.
  - User details for generating email signatures.

---

## Future Enhancements

- **AI-Powered Email Drafting:**
  - Automate email creation using context-aware ML models trained on user activity data.
- **User Activity Tracking:**
  - Track daily activities and create comprehensive JSON reports for training or contextual automation.

---

## Dependencies

Key dependencies include:
- **PyQt5**: For the graphical user interface.
- **SQLite**: To store and manage tasks.
- **Power Automate**: For webhook-based automation.
- **FAISS**: For vector database integration (future scope).

Install all required dependencies:
```bash
pip install -r requirements.txt
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your fork:
   ```bash
   git push origin feature-name
   ```
5. Open a Pull Request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

Special thanks to all contributors and the open-source community for their tools and libraries.

---


To add the generated flow diagram image into your README, you can embed it using Markdown. Here's the updated README snippet with the image included:

---



## Flow Diagram

Below is the flow diagram illustrating the process:

![Flow Diagram](https://www.plantuml.com/plantuml/png/PL4zRzim4DtvAmwPxAb3aGxMq0Jzw5At3fosw7WMdoB258_WdTButvUIx1PmDeBtFkxTkrFZOkCGtVnmRlCz8z7kz62tT9zp32rRaDIupGz58VPUoLYFIi-1oRFs1-7Y6nSwMZtM0N4iO7yYl0GrVRycwv5ezHkwTaIRpx2sfwx8GFk7hy507zdum8fc6kyaZv4Dr0N4wiMZoS0MMexnr3X41Qs-oIIrR1HI7ctPYJoCGrGQE8rdVFAXSvizFsE1cBosFMThQzYQw-P-iSHD3Vr1OaHhLDNE5cmyCVPL-V_F9BkJFoXq8TCl77gHO-CwASTfsvySGyLY8OHqHPZIBwfxOnkLFWqroq8dVkAGviXvbjY6jeXAP_JstIqzXW7Q0pRdfTbmxcChsuj-a4G9yF3NZIoDJz0j9tx2W6HaV6Z-dRX-e2YnMPNdr8AusXI9K5f5i7_J5h19MS-SBqWeR0jAAsKMnnJdgi3zCMGoeOGN8pNaIs5kiolIGfLQ6NB4T1uroUwkpiSX_WK0)

---
