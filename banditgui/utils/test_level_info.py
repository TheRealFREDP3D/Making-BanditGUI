#!/usr/bin/env python3
"""
Test script for the level_info module.

This script demonstrates how to use the level_info module to access
the level information for the Bandit wargame.
"""

import json

# Import level_info from the banditgui package
from banditgui.utils import level_info


def print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2))

def main():
    """Main function to test the level_info module."""
    print("=== Testing level_info module ===\n")

    # Get general information
    print("=== General Information ===")
    general_info = level_info.get_general_info()
    print(f"General info excerpt: {general_info['general'][:100]}...\n")

    # Get available levels
    print("=== Available Levels ===")
    available_levels = level_info.get_available_levels()
    print(f"Available levels: {available_levels}\n")

    # Get information for level 0
    print("=== Level 0 Information ===")
    level_0_info = level_info.get_level_info(0)
    print_json(level_0_info)
    print()

    # Show command links for level 0
    print("=== Level 0 Command Links ===")
    if level_0_info and 'commands_links' in level_0_info:
        print_json(level_0_info['commands_links'])
    print()

    # Show reading links for level 0
    print("=== Level 0 Reading Links ===")
    if level_0_info and 'reading_links' in level_0_info:
        print_json(level_0_info['reading_links'])
    print()

    # Get information for a non-existent level
    print("=== Non-existent Level Information ===")
    non_existent_level = level_info.get_level_info(999)
    print(f"Level 999 info: {non_existent_level}\n")

    print("=== Test completed ===")



if __name__ == "__main__":
    main()
