# Project - BanditGUI

BanditGUI is a web-based tool designed to help users learn and practice security concepts, particularly those found in challenges like the OverTheWire Bandit wargame.

## Table of Contents (TOC)

* [X]**Chapter 1**: Set Up the Basic Flask App (#Chapter-1-set-up-the-basic-flask-app)

[X]Guide
[X]Video
[X]Code

---

* [X]**Chapter 2**: Add the Two-Panel Layout (#Chapter-2-add-the-two-panel-layout)

[X]Guide
[X]Video
[X]Code

---

* []**Chapter 3**: Implement a Simulated Terminal (#Chapter-3-implement-a-simulated-terminal)

[X]Guide
[]Video
[X]Code

---

* []**Chapter 4**: Add Basic SSH Connection (Using Paramiko) (#Chapter-4-add-basic-ssh-connection-using-paramiko)

[X]Guide
[]Video
[X]Code

---

* []**Chapter 5**: Add a Simple AI Chat Assistant (#Chapter-5-add-a-simple-ai-chat-assistant)

[X]Guide
[]Video
[X]Code

---

* []**Chapter 6**: Add Password Management with Encryption (#Chapter-6-add-password-management-with-encryption)

[X]Guide
[]Video
[X]Code

---

* []**Chapter 7**: Add Progress Tracking (#Chapter-7-add-progress-tracking)

[X]Guide
[]Video
[X]Code

---

* []**Chapter 8**: Add Gamification (Badges/Streaks) (#Chapter-8-add-gamification-badgesstreaks)

[X]Guide
[]Video
[X]Code

---

* [X]**Level Data**: Fetching and Managing Level Information (#level-data)

[X]Tool
[X]Documentation

---

## Summary of Each Chapter

**Chapter 1**: Set Up the Basic Flask App
Purpose: Establish the foundation of the web application.
Details: Install the Flask framework and create a simple project structure with a main file (app.py) and a basic HTML template (index.html). When users visit the root URL (/), they see a welcome message displayed on the page.

**Chapter 2**: Add the Two-Panel Layout
Purpose: Design a user-friendly interface with two sections.
Details: Modify the HTML template to include a two-panel layout using Flexbox CSS. The left panel is reserved for chat interactions, while the right panel serves as a terminal interface for command input and output.

**Chapter 3**: Implement a Simulated Terminal
Purpose: Enable users to interact with a terminal-like feature.
Details: Add JavaScript to the frontend to process user-typed commands (e.g., echo). The app simulates terminal behavior by displaying predefined responses in the right panel, mimicking a real terminal.

**Chapter 4**: Add Basic SSH Connection (Using Paramiko)
Purpose: Allow the app to connect to a server via SSH.
Details: Install the Paramiko library and enhance the backend to support SSH connections (e.g., to localhost for testing). Add a button on the frontend to execute SSH commands, with results shown in the terminal panel.

**Chapter 5**: Add a Simple AI Chat Assistant
Purpose: Offer users helpful hints through a chat feature.
Details: Create a JSON file containing predefined hints and update the backend to process chat requests. The frontend sends user queries to the server, and responses are displayed in the left chat panel.

**Chapter 6**: Add Password Management with Encryption
Purpose: Securely manage and store user passwords.
Details: Install the cryptography library and use Fernet encryption to secure passwords. Passwords are encrypted before storage in a file, ensuring they remain protected from unauthorized access.

**Chapter 7**: Add Progress Tracking
Purpose: Monitor and display user progress through levels.
Details: Store completed levels in a JSON file, managed by the backend. The frontend updates to show progress, such as the number of levels completed, providing users with a sense of achievement.

**Chapter 8**: Add Gamification (Badges/Streaks)
Purpose: Increase user engagement with rewards.
Details: Implement logic to award badges (e.g., "First Chapter" for completing level 0) based on user accomplishments. The frontend displays these badges, motivating users to continue progressing.

## Level Data

The application includes a tool to fetch level information from the OverTheWire Bandit website. This data is used to provide users with guidance on how to complete each level.

### Level Data Structure

The level data is stored in JSON format in the `levels_data` directory:

- `general_info.json`: Contains general information about the Bandit wargame
- `levels_info.json`: Contains information for all levels (bandit0 to bandit34)
- `all_data.json`: Contains both general and level-specific information

### Fetching Level Data

To fetch the latest level information from the OverTheWire website, run:

```bash
python levels_data/get_data.py
```

This will:
1. Fetch the main Bandit page to get general information
2. Fetch each level page (bandit0 to bandit34)
3. Extract relevant information (level goal, commands, helpful reading material)
4. Save the data in JSON format in the `levels_data` directory

### Accessing Level Data

You can use the `level_info.py` module to access the level information in your application:

```python
import level_info

# Get general information
general_info = level_info.get_general_info()

# Get a list of available levels
available_levels = level_info.get_available_levels()

# Get information for a specific level
level_0_info = level_info.get_level_info(0)

# Get information for all levels
all_levels_info = level_info.get_all_levels_info()
```

For more details, see the [levels_data/README.md](levels_data/README.md) file.

## Conclusion

This TOC and Chapter-by-Chapter summary provide a clear roadmap for developing BanditGUI, making it accessible for developers to follow and build the application. Each Chapter builds on the previous one, creating a fully functional and engaging tool.
