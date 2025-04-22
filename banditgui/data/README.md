# Bandit Level Data

This directory contains data and tools for fetching and managing level information for the OverTheWire Bandit wargame. The tools allow you to fetch level information from the OverTheWire website and save it in JSON format for use in the BanditGUI application.

## Overview

The OverTheWire Bandit wargame is a series of challenges designed to teach the basics of Linux command line, security concepts, and hacking techniques. Each level presents a specific challenge that must be solved to progress to the next level.

This tool fetches the following information for each level:
- Level goal: What the player needs to accomplish
- Commands: Useful commands that may help solve the level
- Reading material: Helpful resources for learning more about the concepts
- Links: URLs to manual pages and educational resources

## Files

- `get_data.py`: A tool to fetch level information from the OverTheWire website
- `level_info.py`: A module that provides functions to access the level information
- `general_info.json`: Contains general information about the Bandit wargame
- `levels_info.json`: Contains information for all levels (bandit0 to bandit34)
- `all_data.json`: Contains both general and level-specific information

## How to Use

### Fetching Data

To fetch the latest level information from the OverTheWire website, run:

```bash
python get_data.py
```

This will:
1. Fetch the main Bandit page to get general information
2. Fetch each level page (bandit0 to bandit34)
3. Extract relevant information (level goal, commands, helpful reading material)
4. Save the data in JSON format in this directory

### Accessing Data in Your Application

You can use the `level_info.py` module to access the level information in your application:

```python
import level_info

# Get general information
general_info = level_info.get_general_info()
print(f"General info: {general_info['general'][:100]}...")

# Get a list of available levels
available_levels = level_info.get_available_levels()
print(f"Available levels: {available_levels}")

# Get information for a specific level
level_0_info = level_info.get_level_info(0)
print(f"Level 0 goal: {level_0_info['goal']}")

# Access command links for a level
for cmd_link in level_0_info['commands_links']:
    print(f"Command: {cmd_link['text']} - {cmd_link['url']}")

# Access reading material links for a level
for reading_link in level_0_info['reading_links']:
    print(f"Reading: {reading_link['text']} - {reading_link['url']}")

# Get information for all levels
all_levels_info = level_info.get_all_levels_info()
print(f"Total levels: {len(all_levels_info)}")
```

### Displaying Level Information in a User Interface

You can use the level information to create a rich user interface that guides players through the Bandit wargame:

```python
def display_level_info(level_num):
    level_data = level_info.get_level_info(level_num)
    if not level_data:
        return "Level not found"

    output = f"=== LEVEL {level_num} ===\n\n"
    output += f"GOAL:\n{level_data['goal']}\n\n"
    output += f"COMMANDS YOU MAY NEED:\n{level_data['commands']}\n\n"

    # Add links to commands
    if level_data['commands_links']:
        output += "COMMAND REFERENCES:\n"
        for link in level_data['commands_links']:
            output += f"- {link['text']}: {link['url']}\n"
        output += "\n"

    # Add reading material
    if level_data['reading']:
        output += f"HELPFUL READING MATERIAL:\n{level_data['reading']}\n\n"

    # Add links to reading material
    if level_data['reading_links']:
        output += "READING REFERENCES:\n"
        for link in level_data['reading_links']:
            output += f"- {link['text']}: {link['url']}\n"

    return output
```

## Data Structure

### General Information

```json
{
  "general": "Text describing the Bandit wargame..."
}
```

### Level Information

```json
[
  {
    "level": 0,
    "goal": "The goal of this level is...",
    "commands": "Commands you may need: ssh, ...",
    "commands_links": [
      {
        "text": "ssh",
        "url": "https://manpages.ubuntu.com/manpages/noble/man1/ssh.1.html"
      }
    ],
    "reading": "Helpful reading material: ...",
    "reading_links": [
      {
        "text": "Secure Shell (SSH) on Wikipedia",
        "url": "https://en.wikipedia.org/wiki/Secure_Shell"
      },
      {
        "text": "How to use SSH on wikiHow",
        "url": "https://www.wikihow.com/Use-SSH"
      }
    ]
  },
  {
    "level": 1,
    "goal": "The goal of this level is...",
    "commands": "Commands you may need: ls, cd, cat, ...",
    "commands_links": [
      {
        "text": "ls",
        "url": "https://manpages.ubuntu.com/manpages/noble/man1/ls.1.html"
      }
    ],
    "reading": "Helpful reading material: ...",
    "reading_links": []
  },
  ...
]
```

## Implementation Details

### get_data.py

The `get_data.py` script uses the following libraries:
- `requests`: For fetching web pages
- `BeautifulSoup4`: For parsing HTML and extracting information
- `json`: For saving data in JSON format

The script performs the following steps:
1. Fetches the main Bandit page to extract general information
2. Iterates through each level (bandit0 to bandit34)
3. Fetches the level page and extracts:
   - Level goal
   - Commands needed
   - Helpful reading material
   - Links to manual pages and resources
4. Saves the extracted data in JSON format

### level_info.py

The `level_info.py` module provides a simple API for accessing the level information:

- `get_general_info()`: Returns general information about the Bandit wargame
- `get_available_levels()`: Returns a list of available level numbers
- `get_level_info(level)`: Returns information for a specific level
- `get_all_levels_info()`: Returns information for all levels

## Integration with BanditGUI

To integrate the level information with the BanditGUI application:

1. Import the `level_info` module in your application
2. Use the provided functions to access level information
3. Display the information in the chat panel or terminal

Example integration in a Flask route:

```python
@app.route('/level/<int:level_num>')
def get_level(level_num):
    level_data = level_info.get_level_info(level_num)
    if level_data:
        return jsonify(level_data)
    else:
        return jsonify({"error": f"Level {level_num} not found"}), 404
```

## Notes

- The data is fetched from the OverTheWire website and may change over time
- Run `get_data.py` periodically to keep the data up to date
- The script includes a 1-second delay between requests to be nice to the server
- The extracted text may not perfectly match the original formatting
- Links are extracted and stored separately for easy access

## Testing

A test script is provided to verify that the level information can be accessed correctly:

```bash
python test_level_info.py
```

This script demonstrates how to use the `level_info` module and verifies that the data is accessible.

## Troubleshooting

### Missing Dependencies

If you encounter errors related to missing dependencies, install them using pip:

```bash
pip install requests beautifulsoup4
```

### Connection Issues

If the script fails to connect to the OverTheWire website:

1. Check your internet connection
2. Verify that the website is accessible in your browser
3. Try increasing the timeout value in the `fetch_page` function

### Parsing Errors

If the script fails to extract information correctly:

1. Check if the website structure has changed
2. Update the parsing logic in the `parse_level_info` function
3. Run the script with verbose logging for debugging
