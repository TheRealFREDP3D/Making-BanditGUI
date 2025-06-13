#!/usr/bin/env python3
"""
OverTheWire Bandit Level Information Fetcher

This script fetches level information from the OverTheWire Bandit wargame website
and saves it in JSON format for use in the BanditGUI application.

The script fetches:
1. General information from the main Bandit page
2. Level-specific information for each level (bandit0 to bandit34)

The data is saved in JSON files in the levels_data directory.
"""

import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

import requests
from bs4 import BeautifulSoup

# Constants
BASE_URL = "https://overthewire.org/wargames/bandit/"
LEVELS_RANGE = range(0, 35)  # bandit0 to bandit34
OUTPUT_DIR = Path(__file__).parent.parent / "data"
GENERAL_OUTPUT_FILE = OUTPUT_DIR / "general_info.json"
LEVELS_OUTPUT_FILE = OUTPUT_DIR / "levels_info.json"
ALL_DATA_FILE = OUTPUT_DIR / "all_data.json"

# Configure requests session
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
session.headers.update(headers)


def fetch_page(url: str) -> Optional[str]:
    """
    Fetch a web page and return its HTML content.

    Args:
        url: The URL to fetch

    Returns:
        The HTML content of the page, or None if the request failed
    """
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_general_info(html: str) -> Dict[str, str]:
    """
    Parse the general information from the main Bandit page.

    Args:
        html: The HTML content of the main Bandit page

    Returns:
        A dictionary containing the general information
    """
    soup = BeautifulSoup(html, "html.parser")
    content_div = soup.find("div", id="content")

    if not content_div:
        return {"general": "Could not extract general information."}

    # Extract all text from the content div, excluding scripts
    for script in content_div.find_all("script"):
        script.extract()

    # Get the main content text
    general_text = content_div.get_text(strip=True, separator="\n")

    # Clean up the text
    general_text = re.sub(r'\n{3,}', '\n\n', general_text)

    return {"general": general_text}


def parse_level_info(html: str, level: int) -> Dict[str, Union[str, int, List[Dict[str, str]]]]:
    """
    Parse the level information from a level page.

    Args:
        html: The HTML content of the level page
        level: The level number

    Returns:
        A dictionary containing the level information
    """
    soup = BeautifulSoup(html, "html.parser")
    content_div = soup.find("div", id="content")

    if not content_div:
        return {
            "level": level,
            "goal": "Could not extract level information.",
            "commands": "",
            "commands_links": [],
            "reading": "",
            "reading_links": []
        }

    # Extract level goal
    goal_section = content_div.find("h2", id="level-goal")
    goal_text = ""
    if goal_section:
        goal_text = ""
        current = goal_section.next_sibling
        while current and not (hasattr(current, 'name') and current.name == 'h2'):
            if hasattr(current, 'get_text'):
                goal_text += current.get_text(strip=True) + "\n"
            elif isinstance(current, str) and current.strip():
                goal_text += current.strip() + "\n"
            current = current.next_sibling

    # Extract commands and their links
    commands_section = content_div.find("h2", id="commands-you-may-need-to-solve-this-level")
    commands_text = ""
    commands_links = []
    if commands_section:
        commands_text = ""
        current = commands_section.next_sibling
        while current and not (hasattr(current, 'name') and current.name == 'h2'):
            if hasattr(current, 'find_all'):
                # Extract links
                for link in current.find_all('a'):
                    if link.get('href') and link.text:
                        commands_links.append({
                            "text": link.text.strip(),
                            "url": link.get('href')
                        })
                commands_text += current.get_text(strip=True) + "\n"
            elif isinstance(current, str) and current.strip():
                commands_text += current.strip() + "\n"
            current = current.next_sibling

    # Extract helpful reading material and their links
    reading_section = content_div.find("h2", id="helpful-reading-material")
    reading_text = ""
    reading_links = []
    if reading_section:
        reading_text = ""
        current = reading_section.next_sibling
        while current and not (hasattr(current, 'name') and current.name == 'h2'):
            if hasattr(current, 'find_all'):
                # Extract links
                for link in current.find_all('a'):
                    if link.get('href') and link.text:
                        reading_links.append({
                            "text": link.text.strip(),
                            "url": link.get('href')
                        })
                reading_text += current.get_text(strip=True) + "\n"
            elif isinstance(current, str) and current.strip():
                reading_text += current.strip() + "\n"
            current = current.next_sibling

    return {
        "level": level,
        "goal": goal_text.strip(),
        "commands": commands_text.strip(),
        "commands_links": commands_links,
        "reading": reading_text.strip(),
        "reading_links": reading_links
    }


def fetch_all_data() -> Dict[str, Union[Dict, List]]:
    """
    Fetch all data from the OverTheWire Bandit website.

    Returns:
        A dictionary containing all the fetched data
    """
    all_data = {
        "general_info": {},
        "levels_info": []
    }

    # Fetch general information
    print("Fetching general information...")
    general_html = fetch_page(BASE_URL)
    if general_html:
        all_data["general_info"] = parse_general_info(general_html)
        print("General information fetched successfully.")
    else:
        print("Failed to fetch general information.")

    # Fetch level information
    all_data["levels_info"] = []
    for level in LEVELS_RANGE:
        print(f"Fetching information for level {level}...")
        level_url = f"{BASE_URL}bandit{level}.html"
        level_html = fetch_page(level_url)

        if level_html:
            level_info = parse_level_info(level_html, level)
            all_data["levels_info"].append(level_info)
            print(f"Level {level} information fetched successfully.")
        else:
            print(f"Failed to fetch information for level {level}.")

        # Be nice to the server
        time.sleep(1)

    return all_data


def save_data(data: Dict[str, Union[Dict, List]]) -> None:
    """
    Save the fetched data to JSON files.

    Args:
        data: The data to save
    """
    # Save general information
    with open(GENERAL_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data["general_info"], f, indent=2)
    print(f"General information saved to {GENERAL_OUTPUT_FILE}")

    # Save level information
    with open(LEVELS_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data["levels_info"], f, indent=2)
    print(f"Level information saved to {LEVELS_OUTPUT_FILE}")

    # Save all data
    with open(ALL_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"All data saved to {ALL_DATA_FILE}")


def main():
    """Main function to run the script."""
    print("Starting to fetch data from OverTheWire Bandit website...")

    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Fetch and save data
    data = fetch_all_data()
    save_data(data)

    print("Data fetching completed successfully.")


if __name__ == "__main__":
    main()
