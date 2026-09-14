# Helpdesk Automation

A standalone application designed to streamline and automate helpdesk workflows. This tool provides a user-friendly web interface to manage tasks, seamlessly integrating with ServiceNow and local processing scripts.

## ✨ Features

* **Web-Based Dashboard:** A user-friendly GUI that allows users to trigger and monitor automation tasks without needing to use the command line.
* **ServiceNow (SNOW) Integration:** Authenticates securely with your ServiceNow instance to automate ticket management, updates, and workflow execution.
* **Web Browser Automation:** Utilizes an integrated Chrome WebDriver to seamlessly perform UI-level tasks and navigation in the background.
* **Secure Credential Management:** Keeps your system URLs, usernames, and passwords safe via local `.env` configuration, ensuring no sensitive data is hardcoded into the executable.

## 📥 Installation

You do not need to install Python or any programming tools to run this application.

1. Navigate to the [Releases](../../releases) page of this repository.
2. Download the latest `Helpdesk-Automation-vX.X.zip` file.
3. Extract the ZIP file to a location on your computer (e.g., your Desktop or Documents folder). 

## ⚙️ Setup & Configuration

Before running the application for the first time, you must provide your personal credentials so the tool can authenticate with ServiceNow.

1. Open your extracted `Helpdesk-Automation` folder.
2. Locate the file named `.env.example`.
3. Rename this file to exactly `.env` (make sure your operating system doesn't hide the file extension).
4. Open the `.env` file in Notepad or any plain text editor.
5. Fill in your specific details:
   ```env
   SECRET_KEY=create_a_random_secure_password_here
   SNOW_USERNAME=your_username
   SNOW_PASSWORD=your_password

## 🚀 Usage

1. Inside your extracted folder, double-click the `run.exe` executable.
2. A black terminal window will open—this is normal and acts as the application's engine. Keep this window open.
3. The Helpdesk Automation GUI will launch automatically.
4. Use the interface to execute your automated tasks. The application will utilize the bundled Chrome driver and scripts seamlessly in the background.

## 🛠️ Troubleshooting

* **The application immediately closes:** Ensure your `.env` file is named correctly (not `.env.txt`) and that all required fields are filled out. 
* **Errors during automation:** Check the black terminal window. It will display real-time logs and error messages that can help pinpoint if a password was entered incorrectly or if a network timeout occurred.

## 📁 Directory Structure Note

* For the executable to function correctly, do not separate `run.exe` from its accompanying folders. It must remain in the same directory as your `.env` file.

